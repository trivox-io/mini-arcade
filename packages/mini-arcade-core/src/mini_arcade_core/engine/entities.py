from __future__ import annotations

from dataclasses import dataclass

from mini_arcade.utils.logging import logger
from mini_arcade_core.engine.animation import Animation
from mini_arcade_core.engine.components import Anim2D, Life, Sprite2D
from mini_arcade_core.engine.render.style import RenderStyle
from mini_arcade_core.spaces.collision.specs import (
    CircleColliderSpec,
    ColliderSpec,
    LineColliderSpec,
    PolyColliderSpec,
    RectColliderSpec,
)
from mini_arcade_core.spaces.geometry.shapes import (
    Circle,
    Line,
    Poly,
    Rect,
    Shape2D,
    Triangle,
)
from mini_arcade_core.spaces.geometry.size import Size2D
from mini_arcade_core.spaces.geometry.transform import Transform2D
from mini_arcade_core.spaces.math.vec2 import Vec2
from mini_arcade_core.spaces.physics.kinematics2d import Kinematic2D


class EntityIdAllocator:
    """
    Simple entity ID allocator.

    :param start: The starting ID for allocation.
    :type start: int
    """

    def __init__(self, start: int = 1000):
        self._next = start

    def new(self) -> int:
        """
        Allocate a new unique entity ID.

        :return: The allocated entity ID.
        :rtype: int
        """
        eid = self._next
        self._next += 1
        return eid


@dataclass
class BaseEntity:
    """
    Base entity class.

    :ivar id: The unique ID of the entity.
    :ivar name: The optional name of the entity.
    :ivar transform: The transform of the entity.
    :ivar shape: The shape of the entity.
    :ivar style: The render style of the entity.
    :ivar kinematic: The kinematic body of the entity.
    :ivar collider: The collider specification of the entity.
    :ivar sprite: The sprite component of the entity.
    :ivar anim: The animation component of the entity.
    :ivar life: The life component of the entity.
    """

    id: int
    name: str
    codename: str
    transform: Transform2D
    shape: Shape2D
    z_index: int = 0
    rotation_deg: float = 0.0
    style: RenderStyle | None = None

    kinematic: Kinematic2D | None = None
    collider: ColliderSpec | None = None
    sprite: Sprite2D | None = None
    anim: Anim2D | None = None
    life: Life | None = None

    @staticmethod
    def _get_shape_by_kind(kind: str, shape_data: dict) -> Shape2D:
        """
        Get a shape object by its kind and shape data.

        :param kind: The kind of shape (rect, circle, triangle, line, poly).
        :type kind: str
        :param shape_data: The dictionary containing the shape data.
        :type shape_data: dict
        :return: The created shape object.
        :rtype: Shape2D
        """
        shape = Rect(corner_radius=float(shape_data.get("corner_radius", 0.0)))
        if kind == "circle":
            shape = Circle(radius=float(shape_data.get("radius", 0.0)))
        elif kind == "triangle":
            shape = Triangle()
        elif kind == "line":
            # optional support later (needs a/b)
            a = shape_data.get("a", {}) or {}
            b = shape_data.get("b", {}) or {}
            dash = shape_data.get("dash", {}) or {}
            dash_length = dash.get("length", None)
            dash_gap = dash.get("gap", None)
            shape = Line(
                a=Vec2(float(a.get("x", 0.0)), float(a.get("y", 0.0))),
                b=Vec2(float(b.get("x", 0.0)), float(b.get("y", 0.0))),
                dash_length=(
                    float(dash_length) if dash_length is not None else None
                ),
                dash_gap=float(dash_gap) if dash_gap is not None else None,
            )
        elif kind == "poly":
            raw_points = shape_data.get("points") or []
            pts: list[Vec2] = []

            for p in raw_points:
                if isinstance(p, dict):
                    pts.append(
                        Vec2(float(p.get("x", 0.0)), float(p.get("y", 0.0)))
                    )
                else:
                    # allow tuples/lists too
                    x, y = p
                    pts.append(Vec2(float(x), float(y)))

            shape = Poly(points=pts or None)

        return shape

    @classmethod
    def _get_center(cls, transform_data: dict) -> Vec2:
        """
        Get the center position from the entity transform data.

        :param transform_data: The dictionary containing the entity transform data.
        :type transform_data: dict
        :return: The center position as a Vec2 object.
        :rtype: Vec2
        """
        center = transform_data.get("center", {}) or {}
        return Vec2(float(center.get("x", 0.0)), float(center.get("y", 0.0)))

    @classmethod
    def _get_size(cls, transform_data: dict) -> Size2D:
        """
        Get the size from the entity transform data.

        :param transform_data: The dictionary containing the entity transform data.
        :type transform_data: dict
        :return: The size as a Size2D object.
        :rtype: Size2D
        """
        size = transform_data.get("size", {}) or {}
        return Size2D(
            float(size.get("width", 0.0)), float(size.get("height", 0.0))
        )

    @classmethod
    def _get_kinematic(cls, data: dict) -> Kinematic2D | None:
        """
        Get the kinematic body from the entity data.

        :param data: The dictionary containing the entity data.
        :type data: dict
        :return: The kinematic body as a Kinematic2D object.
        :rtype: Kinematic2D
        """
        if data.get("kinematic"):
            k = data["kinematic"]
            vel = k.get("velocity", {}) or {}
            acc = k.get("acceleration", {}) or {}
            return Kinematic2D(
                velocity=Vec2(
                    float(k.get("velocity_x", vel.get("vx", 0.0))),
                    float(k.get("velocity_y", vel.get("vy", 0.0))),
                ),
                accel=Vec2(
                    float(k.get("acceleration_x", acc.get("ax", 0.0))),
                    float(k.get("acceleration_y", acc.get("ay", 0.0))),
                ),
                max_speed=float(k.get("max_speed", 0.0)),
            )
        return None

    @classmethod
    def _get_style(cls, data: dict) -> RenderStyle | None:
        """
        Get the render style from the entity data.

        :param data: The dictionary containing the entity data.
        :type data: dict
        :return: The render style as a RenderStyle object.
        :rtype: RenderStyle
        """
        if data.get("style"):
            st = data["style"]
            return RenderStyle(
                fill=st.get("fill", None),
                stroke=st.get("stroke", None),
            )
        return None

    @classmethod
    def _get_collider(cls, data: dict) -> ColliderSpec | None:
        """
        Get the collider spec from the entity data.

        :param data: The dictionary containing the entity data.
        :type data: dict
        :return: The collider spec.
        :rtype: ColliderSpec | None
        """
        c = data.get("collider", {}) or {}
        if not c:
            return None

        kind = c.get("kind")
        if kind == "rect":
            s = c.get("size", {}) or {}
            size = None
            if s:
                size = Size2D(
                    float(s.get("width", 0.0)),
                    float(s.get("height", 0.0)),
                )
            return RectColliderSpec(size=size)

        if kind == "circle":
            radius = c.get("radius", None)
            return CircleColliderSpec(
                radius=float(radius) if radius is not None else None
            )

        if kind == "line":
            a = c.get("a", {}) or {}
            b = c.get("b", {}) or {}
            return LineColliderSpec(
                a=Vec2(float(a.get("x", 0.0)), float(a.get("y", 0.0))),
                b=Vec2(float(b.get("x", 0.0)), float(b.get("y", 0.0))),
            )

        if kind == "poly":
            raw_points = c.get("points", []) or []
            pts: list[Vec2] = []
            for p in raw_points:
                if isinstance(p, dict):
                    pts.append(
                        Vec2(float(p.get("x", 0.0)), float(p.get("y", 0.0)))
                    )
                else:
                    x, y = p
                    pts.append(Vec2(float(x), float(y)))
            return PolyColliderSpec(points=tuple(pts))

        return None

    @classmethod
    def from_dict(cls, data: dict) -> BaseEntity:
        """
        Create an entity from a dictionary.

        :param data: The dictionary containing the entity data.
        :type data: dict
        :return: The created entity.
        :rtype: BaseEntity
        """
        t = data.get("transform", {}) or {}

        center = cls._get_center(t)
        size = cls._get_size(t)

        shape_data = data.get("shape", {}) or {}
        kind = shape_data.get("kind", "rect")

        shape = cls._get_shape_by_kind(kind, shape_data)
        kinematic = cls._get_kinematic(data)
        collider = cls._get_collider(data)
        style = cls._get_style(data)

        name: str = data.get("name", "")
        codename = name.lower().replace(" ", "_")

        sprite = None
        if data.get("sprite"):
            sprite_data = data["sprite"]
            sprite = Sprite2D(texture=int(sprite_data.get("texture", 0)))

        life = None
        if data.get("life"):
            life_data = data["life"]
            ttl = life_data.get("ttl", None)
            alive = bool(life_data.get("alive", True))
            life = Life(
                ttl=float(ttl) if ttl is not None else None, alive=alive
            )

        anim = None
        if data.get("anim"):
            anim_data = data["anim"]
            frames = anim_data.get("frames", []) or []
            fps = float(anim_data.get("fps", 0.0))
            loop = bool(anim_data.get("loop", False))
            anim = Anim2D(
                anim=Animation(frames=frames, fps=fps, loop=loop),
                texture=frames[0] if frames else None,
            )

        return BaseEntity(
            id=int(data.get("id", 0)),
            name=name,
            codename=codename,
            transform=Transform2D(center=center, size=size),
            shape=shape,
            style=style,
            rotation_deg=float(t.get("rotation_deg", 0.0)),
            kinematic=kinematic,
            collider=collider,
            sprite=sprite,
            anim=anim,
            life=life,
        )

"""
Reusable combat helpers for health, contact damage, and projectile hits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, Iterable, TypeVar

from mini_arcade_core.engine.entities import BaseEntity
from mini_arcade_core.scenes.systems.phases import SystemPhase
from mini_arcade_core.spaces.collision.intersections import intersects_entities

# pylint: disable=invalid-name
TCtx = TypeVar("TCtx")
# pylint: enable=invalid-name


def _default_enabled_when(_ctx: object) -> bool:
    return True


def _default_pair_predicate(
    _ctx: object,
    _attacker: BaseEntity,
    _target: BaseEntity,
) -> bool:
    return True


def _default_entity_predicate(_ctx: object, _entity: BaseEntity) -> bool:
    return True


def _default_hit_predicate(
    _ctx: object,
    _projectile: BaseEntity,
    _target: BaseEntity,
) -> bool:
    return True


def _default_keep_entity(entity: BaseEntity) -> bool:
    life = getattr(entity, "life", None)
    if life is not None:
        return bool(getattr(life, "alive", True))
    return bool(getattr(entity, "alive", True))


def _entity_rect(entity: BaseEntity) -> tuple[float, float, float, float]:
    return (
        float(entity.transform.center.x),
        float(entity.transform.center.y),
        float(entity.transform.size.width),
        float(entity.transform.size.height),
    )


def mark_entity_dead(entity: BaseEntity) -> None:
    """Mark one entity as dead using either ``life.alive`` or ``alive``."""

    life = getattr(entity, "life", None)
    if life is not None:
        setattr(life, "alive", False)
        return
    setattr(entity, "alive", False)


@dataclass
class HealthPool:
    """Mutable hit-point state for one fighter-like entity."""

    current_hp: float
    max_hp: float
    alive: bool = True

    def clamp(self) -> None:
        """
        Clamp current HP to the range [0, max_hp] and update alive status.
        """
        self.max_hp = max(0.0, float(self.max_hp))
        self.current_hp = max(0.0, min(float(self.current_hp), self.max_hp))
        self.alive = bool(self.current_hp > 0.0 and self.alive)


def reflect_from_bounds(
    entity: BaseEntity,
    *,
    bounds: tuple[float, float, float, float],
    bounce_left: bool = True,
    bounce_right: bool = True,
    bounce_top: bool = True,
    bounce_bottom: bool = True,
) -> tuple[str, ...]:
    """Reflect one kinematic entity from an arbitrary axis-aligned rect."""

    if entity.kinematic is None:
        return ()

    bx, by, bw, bh = bounds
    x, y, w, h = _entity_rect(entity)
    hit_sides: list[str] = []

    if bounce_left and x < float(bx):
        entity.transform.center.x = float(bx)
        entity.kinematic.velocity.x = abs(float(entity.kinematic.velocity.x))
        hit_sides.append("left")

    if bounce_right and (x + w) > float(bx + bw):
        entity.transform.center.x = float(bx + bw) - w
        entity.kinematic.velocity.x = -abs(float(entity.kinematic.velocity.x))
        hit_sides.append("right")

    if bounce_top and y < float(by):
        entity.transform.center.y = float(by)
        entity.kinematic.velocity.y = abs(float(entity.kinematic.velocity.y))
        hit_sides.append("top")

    if bounce_bottom and (y + h) > float(by + bh):
        entity.transform.center.y = float(by + bh) - h
        entity.kinematic.velocity.y = -abs(float(entity.kinematic.velocity.y))
        hit_sides.append("bottom")

    return tuple(hit_sides)


@dataclass(frozen=True)
class BoundsBounceBinding(Generic[TCtx]):
    """Declarative bounce rule constrained to an arbitrary bounds rect."""

    entities_getter: Callable[[TCtx], Iterable[BaseEntity]]
    bounds_getter: Callable[[TCtx], tuple[float, float, float, float]]
    predicate: Callable[[TCtx, BaseEntity], bool] = _default_entity_predicate
    bounce_left: bool = True
    bounce_right: bool = True
    bounce_top: bool = True
    bounce_bottom: bool = True
    on_bounce: Callable[[TCtx, BaseEntity, tuple[str, ...]], None] | None = (
        None
    )


@dataclass
class BoundsBounceSystem(Generic[TCtx]):
    """Reflect entities from a configurable axis-aligned arena/bounds rect."""

    name: str = "common_bounds_bounce"
    phase: int = SystemPhase.SIMULATION
    order: int = 40
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[BoundsBounceBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """
        For each binding, reflect each reported entity from the reported bounds
        rect when they intersect, respecting the binding predicate.

        :param ctx: The system context, passed to all binding getters.
        :type ctx: TCtx
        """
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            bounds = binding.bounds_getter(ctx)
            for entity in binding.entities_getter(ctx):
                if not binding.predicate(ctx, entity):
                    continue
                sides = reflect_from_bounds(
                    entity,
                    bounds=bounds,
                    bounce_left=binding.bounce_left,
                    bounce_right=binding.bounce_right,
                    bounce_top=binding.bounce_top,
                    bounce_bottom=binding.bounce_bottom,
                )
                if sides and binding.on_bounce is not None:
                    binding.on_bounce(ctx, entity, sides)


def heal_health_pool(pool: HealthPool, amount: float) -> float:
    """Heal one pool and return the actual restored amount."""

    if not pool.alive or amount <= 0.0:
        return 0.0
    before = float(pool.current_hp)
    pool.current_hp = min(float(pool.max_hp), before + float(amount))
    pool.clamp()
    return max(0.0, float(pool.current_hp) - before)


def damage_health_pool(pool: HealthPool, amount: float) -> float:
    """Damage one pool and return the actual damage applied."""

    if not pool.alive or amount <= 0.0:
        return 0.0
    before = float(pool.current_hp)
    pool.current_hp = max(0.0, before - float(amount))
    pool.alive = bool(pool.current_hp > 0.0)
    pool.clamp()
    return max(0.0, before - float(pool.current_hp))


@dataclass(frozen=True)
class ContactDamageBinding(Generic[TCtx]):
    """Directional contact-damage rule between overlapping entities."""

    attackers_getter: Callable[[TCtx], Iterable[BaseEntity]]
    targets_getter: Callable[[TCtx], Iterable[BaseEntity]]
    health_getter: Callable[[TCtx, BaseEntity], HealthPool | None]
    damage_getter: Callable[[TCtx, BaseEntity, BaseEntity], float]
    predicate: Callable[[TCtx, BaseEntity, BaseEntity], bool] = (
        _default_pair_predicate
    )
    cooldown_seconds: float = 0.3
    on_damage: Callable[[TCtx, BaseEntity, BaseEntity, float], None] | None = (
        None
    )


@dataclass
class ContactDamageSystem(Generic[TCtx]):
    """Apply collision-triggered damage with per-pair cooldowns."""

    name: str = "common_contact_damage"
    phase: int = SystemPhase.SIMULATION
    order: int = 42
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ContactDamageBinding[TCtx], ...] = ()
    _cooldowns: dict[tuple[int, int, int], float] = field(
        init=False,
        default_factory=dict,
        repr=False,
    )

    def _tick_cooldowns(self, dt: float) -> None:
        if not self._cooldowns:
            return
        survivors: dict[tuple[int, int, int], float] = {}
        for key, remaining in self._cooldowns.items():
            next_remaining = float(remaining) - dt
            if next_remaining > 0.0:
                survivors[key] = next_remaining
        self._cooldowns = survivors

    # pylint: disable=too-many-branches
    def step(self, ctx: TCtx) -> None:
        """
        For each binding, apply damage from each reported attacker to each
        reported target when they intersect, respecting the binding predicate and
        per-pair cooldowns.

        :param ctx: The system context, passed to all binding getters.
        :type ctx: TCtx
        """
        if not self.enabled_when(ctx):
            return

        self._tick_cooldowns(max(0.0, float(getattr(ctx, "dt", 0.0))))

        for binding_index, binding in enumerate(self.bindings):
            attackers = tuple(binding.attackers_getter(ctx))
            targets = tuple(binding.targets_getter(ctx))
            if not attackers or not targets:
                continue

            for attacker in attackers:
                if not _default_keep_entity(attacker):
                    continue
                for target in targets:
                    if attacker is target or not _default_keep_entity(target):
                        continue
                    if not binding.predicate(ctx, attacker, target):
                        continue
                    if not intersects_entities(attacker, target):
                        continue

                    pair_key = (
                        int(binding_index),
                        int(attacker.id),
                        int(target.id),
                    )
                    if self._cooldowns.get(pair_key, 0.0) > 0.0:
                        continue

                    health = binding.health_getter(ctx, target)
                    if health is None or not health.alive:
                        continue
                    damage = max(
                        0.0,
                        float(binding.damage_getter(ctx, attacker, target)),
                    )
                    if damage <= 0.0:
                        continue

                    applied = damage_health_pool(health, damage)
                    self._cooldowns[pair_key] = max(
                        0.0, float(binding.cooldown_seconds)
                    )
                    if applied > 0.0 and binding.on_damage is not None:
                        binding.on_damage(ctx, attacker, target, applied)


@dataclass(frozen=True)
class ProjectileHitBinding(Generic[TCtx]):
    """Projectile-vs-target hit rule."""

    projectiles_getter: Callable[[TCtx], Iterable[BaseEntity]]
    targets_getter: Callable[[TCtx], Iterable[BaseEntity]]
    health_getter: Callable[[TCtx, BaseEntity], HealthPool | None]
    damage_getter: Callable[[TCtx, BaseEntity, BaseEntity], float]
    predicate: Callable[[TCtx, BaseEntity, BaseEntity], bool] = (
        _default_hit_predicate
    )
    destroy_on_hit: bool = True
    on_hit: Callable[[TCtx, BaseEntity, BaseEntity, float], None] | None = None


@dataclass
class ProjectileHitSystem(Generic[TCtx]):
    """Apply damage when projectile-like entities intersect live targets."""

    name: str = "common_projectile_hit"
    phase: int = SystemPhase.SIMULATION
    order: int = 44
    enabled_when: Callable[[TCtx], bool] = _default_enabled_when
    bindings: tuple[ProjectileHitBinding[TCtx], ...] = ()

    def step(self, ctx: TCtx) -> None:
        """
        For each binding, apply damage from each reported projectile to each
        reported target when they intersect, respecting the binding predicate and
        optionally destroying the projectile on hit.

        :param ctx: The system context, passed to all binding getters.
        :type ctx: TCtx
        """
        if not self.enabled_when(ctx):
            return

        for binding in self.bindings:
            for projectile in tuple(binding.projectiles_getter(ctx)):
                if not _default_keep_entity(projectile):
                    continue
                for target in tuple(binding.targets_getter(ctx)):
                    if not _default_keep_entity(target):
                        continue
                    if not binding.predicate(ctx, projectile, target):
                        continue
                    if not intersects_entities(projectile, target):
                        continue

                    health = binding.health_getter(ctx, target)
                    if health is None or not health.alive:
                        continue

                    damage = max(
                        0.0,
                        float(binding.damage_getter(ctx, projectile, target)),
                    )
                    if damage <= 0.0:
                        continue

                    applied = damage_health_pool(health, damage)
                    if applied > 0.0 and binding.on_hit is not None:
                        binding.on_hit(ctx, projectile, target, applied)
                    if binding.destroy_on_hit:
                        mark_entity_dead(projectile)
                    break


__all__ = [
    "BoundsBounceBinding",
    "BoundsBounceSystem",
    "ContactDamageBinding",
    "ContactDamageSystem",
    "HealthPool",
    "ProjectileHitBinding",
    "ProjectileHitSystem",
    "damage_health_pool",
    "heal_health_pool",
    "mark_entity_dead",
    "reflect_from_bounds",
]

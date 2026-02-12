# tools/subtree-push.ps1
$ErrorActionPreference = "Stop"

git subtree push --prefix=packages/mini-arcade-core pkg-core main
git subtree push --prefix=packages/mini-arcade-pygame-backend pkg-pygame main
git subtree push --prefix=packages/mini-arcade-native-backend pkg-native main

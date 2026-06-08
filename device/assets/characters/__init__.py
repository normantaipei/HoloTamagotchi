# assets/characters — 角色註冊表。
# 新增角色：複製 marine/ 改成新角色資料夾、改 character.py，再到這裡 import + 註冊。
# AssetManager 只依賴 REGISTRY。

from .marine import character as marine

REGISTRY = {
    "marine": marine,
}

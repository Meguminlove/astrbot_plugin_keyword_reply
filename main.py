from astrbot.api.all import *
from astrbot.api.event.filter import command, permission_type, event_message_type, EventMessageType, PermissionType
import json
import logging
import os

logger = logging.getLogger("KeywordReplyPlugin")

@register(
    "自定义回复插件",
    "腾讯元宝",
    "智能关键词回复插件",
    "v1.1.0"
)
class KeywordReplyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 修复：手动创建插件数据目录
        plugin_data_dir = os.path.join("data", "plugins", "astrbot_plugin_keyword_reply")
        os.makedirs(plugin_data_dir, exist_ok=True)
        self.config_path = os.path.join(plugin_data_dir, "keyword_reply_config.json")
        self.keyword_map = self._load_config()
        logger.info(f"配置文件路径：{self.config_path}")

    def _load_config(self) -> dict:
        """加载本地配置文件"""
        try:
            if not os.path.exists(self.config_path):
                return {}
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"配置加载失败: {str(e)}")
            return {}

    def _save_config(self, data: dict):
        """保存配置到文件"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"配置保存失败: {str(e)}")

    @command("添加自定义回复")
    @permission_type(PermissionType.ADMIN)
    async def add_reply(self, event: AstrMessageEvent, keyword: str, reply: str):
        """/添加自定义回复 关键字 内容"""
        self.keyword_map[keyword.strip().lower()] = reply
        self._save_config(self.keyword_map)
        yield event.plain_result(f"✅ 已添加关键词回复： [{keyword}] -> {reply}")

    @command("查看自定义回复")
    async def list_replies(self, event: AstrMessageEvent):
        """查看所有关键词回复"""
        if not self.keyword_map:
            yield event.plain_result("暂无自定义回复")
            return
        msg = "当前关键词回复列表：\n" + "\n".join(
            [f"{i+1}. [{k}] -> {v}" for i, (k, v) in enumerate(self.keyword_map.items())]
        )
        yield event.plain_result(msg)

    @command("删除自定义回复")
    @permission_type(PermissionType.ADMIN)
    async def delete_reply(self, event: AstrMessageEvent, keyword: str):
        """/删除自定义回复 关键字 """
        keyword = keyword.strip().lower()
        if keyword not in self.keyword_map:
            yield event.plain_result(f"❌ 未找到关键词：{keyword}")
            return
        del self.keyword_map[keyword]
        self._save_config(self.keyword_map)
        yield event.plain_result(f"✅ 已删除关键词：{keyword}")

    @event_message_type(EventMessageType.ALL)
    async def handle_message(self, event: AstrMessageEvent):
        msg = event.message_str.strip().lower()
        if reply := self.keyword_map.get(msg):
            yield event.plain_result(reply)
            return
        for keyword, reply in self.keyword_map.items():
            if keyword in msg:
                yield event.plain_result(reply)
                return
"""
十问歌问诊数据定义
==================

十问维度、选项、默认值、步骤条配置。
"""

TEN_ASKS = [
    {
        "key": "cold_heat",
        "label": "寒热",
        "icon": "🌡️",
        "question": "您有怕冷或发热的感觉吗？",
        "options": ["正常", "恶寒（怕冷）", "发热", "往来寒热", "畏寒（怕冷加衣可减）", "五心烦热"],
        "stage": 1,
    },
    {
        "key": "sweat",
        "label": "汗",
        "icon": "💧",
        "question": "您出汗情况如何？",
        "options": ["正常", "无汗", "自汗（不活动也出汗）", "盗汗（睡中出汗）", "大汗", "局部出汗"],
        "stage": 1,
    },
    {
        "key": "head_body",
        "label": "头身",
        "icon": "🧠",
        "question": "头部或身体有不适吗？（可多选）",
        "options": ["无不适", "头痛", "头晕", "身痛", "关节痛", "腰痛", "四肢不适", "颈项强痛"],
        "multi": True,
        "stage": 1,
    },
    {
        "key": "stool_urine",
        "label": "二便",
        "icon": "🚽",
        "question": "大小便情况如何？",
        "sub_asks": [
            {"key": "stool", "label": "大便", "options": ["正常", "便秘", "溏泄", "干稀不调", "便血", "里急后重"]},
            {"key": "urine", "label": "小便", "options": ["正常", "清长", "短赤", "频数", "涩痛", "夜尿多"]},
        ],
        "stage": 2,
    },
    {
        "key": "diet_taste",
        "label": "饮食口味",
        "icon": "🍽️",
        "question": "饮食和口味如何？",
        "sub_asks": [
            {"key": "appetite", "label": "食欲", "options": ["正常", "食欲不振", "消谷善饥（易饿）", "厌食油腻", "恶心欲呕"]},
            {"key": "thirst", "label": "口渴", "options": ["正常", "口渴喜冷饮", "口渴喜热饮", "口不渴", "但欲漱水不欲咽"]},
            {"key": "taste", "label": "口味", "options": ["正常", "口苦", "口淡", "口甜", "口酸", "口咸", "口臭"]},
        ],
        "stage": 2,
    },
    {
        "key": "chest_abdomen",
        "label": "胸腹",
        "icon": "🫁",
        "question": "胸腹部有不适吗？（可多选）",
        "options": ["无不适", "胸闷", "心悸", "胁痛", "腹胀", "腹痛", "胃脘不适", "气短"],
        "multi": True,
        "stage": 2,
    },
    {
        "key": "ear_eye",
        "label": "耳目",
        "icon": "👂",
        "question": "耳、目有不适吗？（可多选）",
        "options": ["无不适", "耳鸣", "耳聋", "目眩", "目赤", "视物模糊", "目干涩"],
        "multi": True,
        "stage": 3,
    },
    {
        "key": "sleep",
        "label": "睡眠",
        "icon": "😴",
        "question": "睡眠情况如何？",
        "options": ["正常", "失眠（入睡困难）", "多梦", "易醒", "嗜睡", "彻夜不眠"],
        "stage": 3,
    },
    {
        "key": "old_disease",
        "label": "旧病",
        "icon": "📋",
        "question": "有既往病史吗？",
        "input_type": "text",
        "placeholder": "如：高血压 5 年、糖尿病、手术史等",
        "stage": 3,
    },
    {
        "key": "cause",
        "label": "病因",
        "icon": "🔍",
        "question": "发病可能由什么引起？",
        "options": ["不清楚", "外感（受凉/受风）", "情志（生气/压力）", "饮食不节", "劳倦过度", "外伤"],
        "stage": 3,
    },
]

MENSTRUATION_ASK = {
    "key": "menstruation",
    "label": "经期",
    "icon": "🌸",
    "question": "月经情况如何？",
    "sub_asks": [
        {"key": "cycle", "label": "周期", "options": ["正常", "先期（提前）", "后期（推后）", "不定期"]},
        {"key": "flow", "label": "经量", "options": ["正常", "过多", "过少", "闭经", "崩漏"]},
        {"key": "color", "label": "颜色", "options": ["正常", "淡红", "深红", "紫暗", "有血块"]},
        {"key": "pain", "label": "痛经", "options": ["无", "经前痛", "经期痛", "经后痛"]},
    ],
    "stage": 3,
}

TONGUE_ASK = {
    "key": "tongue_sign",
    "label": "舌诊",
    "icon": "👅",
    "question": "请描述舌象（可参考镜子观察）",
    "input_type": "text",
    "placeholder": "如：舌淡红、苔薄白；或舌红、苔黄腻...",
    "stage": 3,
}

PULSE_ASK = {
    "key": "pulse_sign",
    "label": "脉诊",
    "icon": "🫀",
    "question": "请描述脉象",
    "options": ["不清楚", "浮脉", "沉脉", "迟脉", "数脉", "弦脉", "滑脉", "细脉", "弱脉", "涩脉", "紧脉"],
    "stage": 3,
}

ALL_ASKS = TEN_ASKS + [MENSTRUATION_ASK, TONGUE_ASK, PULSE_ASK]

DEFAULT_TEN_ASKS = {
    "cold_heat": {"type": "", "detail": ""},
    "sweat": {"type": "", "detail": ""},
    "head_body": {"parts": [], "detail": ""},
    "stool_urine": {"stool": "", "urine": "", "detail": ""},
    "diet_taste": {"appetite": "", "thirst": "", "taste": "", "detail": ""},
    "chest_abdomen": {"parts": [], "detail": ""},
    "ear_eye": {"symptoms": [], "detail": ""},
    "sleep": {"quality": "", "detail": ""},
    "old_disease": "",
    "cause": "",
    "menstruation": None,
}

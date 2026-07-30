"""演示病例与检索评测样本。"""

DEMO_CASES = [
    {
        "name": "低风险信息较完整病例",
        "chief_complaint": "头痛恶寒两天，鼻塞流清涕",
        "symptoms": ["恶寒", "无汗", "头身疼痛", "鼻塞流清涕"],
        "tongue": "舌苔薄白",
        "pulse": "脉浮紧",
        "expected_ids": ["syndrome:太阳伤寒证", "formula:麻黄汤"],
    },
    {
        "name": "信息不足需要追问病例",
        "chief_complaint": "咳嗽一周",
        "symptoms": ["咳嗽", "痰多"],
        "tongue": "",
        "pulse": "",
        "expected_ids": ["syndrome:痰湿蕴肺证", "formula:二陈汤"],
    },
    {
        "name": "急症安全拦截病例",
        "chief_complaint": "突发胸痛伴呼吸困难",
        "symptoms": ["胸痛", "呼吸困难", "大汗"],
        "tongue": "",
        "pulse": "",
        "expected_ids": [],
    },
]


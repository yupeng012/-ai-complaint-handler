#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 AI 智能分析模块
功能：
1. 情绪分析 (愤怒/失望/疑惑)
2. 关键信息提取 (订单号/问题类型/诉求)
3. 智能回复生成 (共情型/专业型/补偿型)

使用 MiniMax/DeepSeek API 进行精准分析
"""

import os
import requests
import json
from typing import Dict, List, Optional

class AIComplaintAnalyzer:
    """AI 投诉分析器"""
    
    def __init__(self, api_key: Optional[str] = None, use_mock: bool = False):
        """
        初始化分析器
        
        Args:
            api_key: MiniMax API Key (如果为 None，则使用环境变量 MINIMAX_API_KEY)
            use_mock: 是否使用模拟数据 (用于测试)
        """
        self.api_key = api_key or os.getenv('MINIMAX_API_KEY', '')
        self.use_mock = use_mock or not self.api_key
        
        # API 端点
        self.api_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        
        # 如果既没有 API Key 也没有设置模拟模式，则自动降级到规则引擎
        if not self.api_key and not use_mock:
            print("⚠️ 未检测到 MINIMAX_API_KEY，将使用规则引擎降级方案")
            self.use_mock = True
    
    def analyze(self, text: str) -> Dict:
        """
        分析投诉内容
        
        Args:
            text: 投诉文本
            
        Returns:
            分析结果字典
        """
        if self.use_mock or not self.api_key:
            return self._analyze_with_rules(text)
        
        try:
            return self._analyze_with_ai(text)
        except Exception as e:
            print(f"⚠️ AI 分析失败，降级到规则引擎：{e}")
            return self._analyze_with_rules(text)
    
    def _analyze_with_ai(self, text: str) -> Dict:
        """使用 AI 进行分析"""
        
        # 构建提示词
        prompt = f"""
请分析以下客户投诉内容，并以 JSON 格式返回分析结果。

投诉内容：
{text}

请严格按照以下 JSON 格式返回结果 (不要包含 Markdown 格式，只返回纯 JSON)：
{{
    "emotion": "情绪类型 (从'愤怒'、'失望'、'疑惑'中选择一个)",
    "emotion_reason": "判断该情绪的理由",
    "order_number": "订单号 (如果没有则填'未识别')",
    "problem_type": "问题类型 (从'物流问题'、'质量问题'、'退款问题'、'服务态度'、'产品功能'、'其他'中选择一个)",
    "problem_summary": "问题简述 (20 字以内)",
    "customer_demand": "客户诉求 (如退款/换货/道歉等)",
    "urgency": "紧急程度 (高/中/低)"
}}
"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "MiniMaxAI-01",  # 或使用 "deepseek-chat"
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的客服投诉分析专家，擅长从投诉内容中准确识别客户情绪、提取关键信息并总结问题。请只返回 JSON 格式的分析结果，不要包含任何 Markdown 格式。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        
        # 解析返回的 JSON
        ai_response = result['choices'][0]['message']['content']
        
        # 清理可能的 Markdown 格式
        ai_response = ai_response.replace('```json', '').replace('```', '').strip()
        
        analysis = json.loads(ai_response)
        
        # 添加情绪标签
        emotion_map = {
            '愤怒': '😠 愤怒',
            '失望': '😞 失望',
            '疑惑': '😕 疑惑'
        }
        analysis['emotion_label'] = emotion_map.get(analysis.get('emotion', '疑惑'), '😕 疑惑')
        
        return analysis
    
    def _analyze_with_rules(self, text: str) -> Dict:
        """使用规则引擎进行分析 (降级方案)"""
        text_lower = text.lower()
        
        # 情绪分析
        if any(word in text_lower for word in ['愤怒', '生气', 'fuck', 'terrible', 'horrible', '气死', '混蛋']):
            emotion = '愤怒'
            emotion_label = '😠 愤怒'
            emotion_reason = '检测到强烈情绪化词汇'
        elif any(word in text_lower for word in ['失望', 'disappointed', 'unfortunate', 'sad', '心寒', '无语']):
            emotion = '失望'
            emotion_label = '😞 失望'
            emotion_reason = '检测到失望情绪词汇'
        else:
            emotion = '疑惑'
            emotion_label = '😕 疑惑'
            emotion_reason = '未检测到明显情绪倾向'
        
        # 提取订单号
        import re
        order_match = re.search(r'[订单单号货号订单编][# 编:\s]?([A-Z0-9]{6,})', text, re.IGNORECASE)
        order_number = order_match.group(1) if order_match else '未识别'
        
        # 问题类型
        problem_keywords = {
            '物流问题': ['物流', '快递', '配送', '送达', 'shipping', 'delivery', '没收', '慢'],
            '质量问题': ['质量', '损坏', '破损', '缺陷', 'quality', 'broken', '划痕', '坏的', '故障'],
            '退款问题': ['退款', '退货', '退钱', 'refund', 'return', '赔'],
            '服务态度': ['态度', '客服', '服务', 'service', 'attitude', '素质', '差'],
            '产品功能': ['功能', '使用', '操作', 'function', 'feature', '不会用', '复杂']
        }
        
        problem_type = '其他'
        for p_type, keywords in problem_keywords.items():
            if any(kw in text_lower for kw in keywords):
                problem_type = p_type
                break
        
        # 问题总结
        problem_summary = f"{problem_type}投诉"
        
        # 客户诉求
        if '退款' in text or '退钱' in text:
            customer_demand = '退款'
        elif '换货' in text or '更换' in text:
            customer_demand = '换货'
        elif '道歉' in text:
            customer_demand = '道歉'
        else:
            customer_demand = '解决问题'
        
        # 紧急程度
        if any(word in text_lower for word in ['立即', '马上', '尽快', '投诉', '曝光']):
            urgency = '高'
        elif any(word in text_lower for word in ['希望', '尽快', '及时']):
            urgency = '中'
        else:
            urgency = '低'
        
        return {
            'emotion': emotion,
            'emotion_label': emotion_label,
            'emotion_reason': emotion_reason,
            'order_number': order_number,
            'problem_type': problem_type,
            'problem_summary': problem_summary,
            'customer_demand': customer_demand,
            'urgency': urgency
        }
    
    def generate_responses(self, text: str, analysis: Dict) -> Dict[str, str]:
        """
        生成三种回复草稿
        
        Args:
            text: 原始投诉文本
            analysis: 分析结果
            
        Returns:
            包含三种回复的字典
        """
        
        if self.api_key and not self.use_mock:
            try:
                return self._generate_with_ai(text, analysis)
            except Exception as e:
                print(f"⚠️ AI 生成失败，使用模板生成：{e}")
        
        return self._generate_with_templates(analysis)
    
    def _generate_with_ai(self, text: str, analysis: Dict) -> Dict[str, str]:
        """使用 AI 生成回复"""
        
        responses = {}
        styles = {
            'empathy': '共情型回复：先充分表达理解和歉意，安抚客户情绪，语气要温暖真诚',
            'professional': '专业型回复：直接了当，聚焦事实，逻辑清晰，语气专业冷静',
            'compensation': '补偿型回复：主动提供补偿方案，表达诚意，语气要诚恳并体现重视'
        }
        
        for style, instruction in styles.items():
            prompt = f"""
请根据以下投诉内容和分析结果，撰写一封客服回复邮件。

投诉内容：
{text}

分析结果：
- 情绪：{analysis.get('emotion', '')}
- 问题类型：{analysis.get('problem_type', '')}
- 订单号：{analysis.get('order_number', '未知')}
- 客户诉求：{analysis.get('customer_demand', '')}

回复要求：
{instruction}

请直接回复邮件内容，不需要标题，300 字以内。
"""
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "MiniMaxAI-01",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的客服专家，擅长处理各种客户投诉，能够根据不同场景撰写得体、专业的回复邮件。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 400
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            responses[style] = ai_response
        
        return responses
    
    def _generate_with_templates(self, analysis: Dict) -> Dict[str, str]:
        """使用模板生成回复 (降级方案)"""
        
        order_num = analysis.get('order_number', '未知')
        problem_type = analysis.get('problem_type', '问题')
        customer_demand = analysis.get('customer_demand', '解决问题')
        
        empathy = f"""尊敬的客户，您好！

非常感谢您抽出时间向我们反馈问题。我完全理解您现在的心情，遇到这样的情况，换作是我也会很着急。

关于您提到的订单 {order_num} 的{problem_type}问题，我们非常重视。请您放心，我们已经成立专门小组在核查此事，会在 24 小时内给您一个满意的答复。

您的满意对我们至关重要，我们一定会负责到底！

此致
敬礼

客户关怀团队"""

        professional = f"""尊敬的客户：

您好！感谢您反馈订单 {order_num} 的{problem_type}问题。

经初步核查：
1. 问题类型：{problem_type}
2. 订单状态：正在核查中
3. 处理时限：24 小时内

解决方案：
- 立即安排专人核实情况
- 根据核实结果提供解决方案
- 全程跟进至问题彻底解决

如有任何疑问，请随时与我们联系。

客户服务部
{datetime.now().strftime('%Y-%m-%d')}"""

        compensation = f"""尊敬的客户，您好！

非常抱歉给您带来了不好的体验！关于您反馈的订单 {order_num} 的{problem_type}问题，我们深感歉意。

为表达我们的诚意，我们愿为您提供以下补偿方案：
1. 全额退款 / 重新发货 (视情况而定)
2. 50 元优惠券 (无门槛)
3. VIP 专属客服优先处理

我们深知再多的补偿也无法完全弥补您此次的不愉快体验，但请您相信，我们改进的决心是真诚的。

期待能有机会继续为您服务！

客户关怀团队
24 小时服务热线：400-XXX-XXXX"""

        return {
            'empathy': empathy,
            'professional': professional,
            'compensation': compensation
        }

# 测试
if __name__ == "__main__":
    analyzer = AIComplaintAnalyzer(use_mock=True)
    test_text = "我于 2026-05-01 购买的订单#A12345678 商品，收到后发现严重质量问题！我非常失望！要求立即退款！"
    result = analyzer.analyze(test_text)
    print("分析结果:", json.dumps(result, ensure_ascii=False, indent=2))

"""
Sentiment Analyzer for Vietnamese Financial News
Uses lexicon-based approach with financial domain-specific terms
Returns score from -10 (very negative) to +10 (very positive)
"""

# Vietnamese financial sentiment lexicon
POSITIVE_WORDS = {
    # Price movement
    'tăng': 2, 'tăng giá': 3, 'tăng mạnh': 4, 'tăng trưởng': 3, 'tăng cao': 3,
    'lên cao': 2, 'tăng vọt': 4, 'bứt phá': 4, 'đột phá': 4,
    
    # Performance
    'lợi nhuận': 2, 'lãi': 2, 'hiệu quả': 2, 'thành công': 3, 'khả quan': 3,
    'tích cực': 3, 'phát triển': 2, 'cải thiện': 2, 'tốt': 2, 'tăng trưởng': 3,
    
    # Market sentiment
    'lạc quan': 3, 'hy vọng': 2, 'tin tưởng': 2, 'tiềm năng': 2, 'cơ hội': 2,
    'thuận lợi': 2, 'hấp dẫn': 2, 'sôi động': 2,
    
    # Business
    'đầu tư': 1, 'mở rộng': 2, 'tăng cường': 2, 'nâng cao': 2, 'ký kết': 1,
    'hợp tác': 1, 'thỏa thuận': 1, 'dự án': 1,
}

NEGATIVE_WORDS = {
    # Price movement
    'giảm': -2, 'giảm giá': -3, 'giảm mạnh': -4, 'sụt giảm': -4, 'rớt giá': -4,
    'giảm sâu': -4, 'lao dốc': -5, 'sập': -5, 'rơi': -3,
    
    # Performance  
    'lỗ': -3, 'thua lỗ': -4, 'kém': -2, 'yếu': -2, 'xấu': -3, 'kém hiệu quả': -3,
    'thất bại': -4, 'khó khăn': -2, 'trì trệ': -2,
    
    # Market sentiment
    'bi quan': -3, 'lo ngại': -2, 'rủi ro': -2, 'bất ổn': -3, 'khủng hoảng': -5,
    'suy thoái': -4, 'đình trệ': -3, 'chững lại': -2,
    
    # Business
    'sa thải': -3, 'phá sản': -5, 'nợ': -2, 'vỡ nợ': -5, 'thua kiện': -3,
    'vi phạm': -3, 'điều tra': -2, 'hủy bỏ': -2,
}

# Intensifiers
INTENSIFIERS = {
    'rất': 1.5, 'cực': 2.0, 'quá': 1.5, 'hết sức': 1.8,
    'đặc biệt': 1.3, 'vô cùng': 2.0, 'cực kỳ': 2.0,
}

# Negation words
NEGATIONS = ['không', 'chưa', 'chẳng', 'không có']


def calculate_sentiment_score(text: str) -> float:
    """
    Calculate sentiment score for Vietnamese financial text
    
    Args:
        text: Vietnamese text (title + content)
        
    Returns:
        float: Score from -10 to +10
    """
    if not text or not isinstance(text, str):
        return 0.0
    
    text_lower = text.lower()
    words = text_lower.split()
    
    score = 0.0
    i = 0
    
    while i < len(words):
        word = words[i]
        
        # Check for intensifier
        intensifier = 1.0
        if word in INTENSIFIERS:
            intensifier = INTENSIFIERS[word]
            i += 1
            if i >= len(words):
                break
            word = words[i]
        
        # Check for negation
        negation = False
        if i > 0 and words[i-1] in NEGATIONS:
            negation = True
        
        # Calculate score
        if word in POSITIVE_WORDS:
            word_score = POSITIVE_WORDS[word] * intensifier
            score += -word_score if negation else word_score
            
        elif word in NEGATIVE_WORDS:
            word_score = NEGATIVE_WORDS[word] * intensifier
            score += -word_score if negation else word_score
        
        i += 1
    
    # Normalize to -10 to +10 range
    score = max(-10, min(10, score))
    
    return round(score, 2)


def classify_sentiment(score: float) -> str:
    """Classify sentiment score into category"""
    if score >= 3:
        return 'very_positive'
    elif score >= 1:
        return 'positive'
    elif score >= -1:
        return 'neutral'
    elif score >= -3:
        return 'negative'
    else:
        return 'very_negative'


# Test function
if __name__ == "__main__":
    test_texts = [
        "Cổ phiếu tăng mạnh nhờ lợi nhuận vượt kỳ vọng",
        "Thị trường giảm sâu do lo ngại lạm phát",
        "VN-Index tăng nhẹ trong phiên giao dịch",
        "Công ty báo cáo thua lỗ quý 3",
        "Nhà đầu tư lạc quan về triển vọng tăng trưởng",
    ]
    
    for text in test_texts:
        score = calculate_sentiment_score(text)
        category = classify_sentiment(score)
        print(f"Text: {text}")
        print(f"Score: {score} ({category})\n")

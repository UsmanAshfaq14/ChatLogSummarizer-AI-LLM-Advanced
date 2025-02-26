import json
import csv
import re
from io import StringIO

class ChatLogSummarizer:
    def __init__(self):
        # Define word lists for sentiment analysis
        self.positive_words = ["happy", "great", "satisfied", "good", "excellent"]
        self.negative_words = ["problem", "issue", "complaint", "bad", "unsatisfied"]
        
        # Define category keywords
        self.category_keywords = {
            "Critique": ["criticize", "dislike", "disappointed"],
            "Feedback": ["feedback", "suggestion", "input"],
            "Positive Response": ["thank you", "great", "happy", "appreciate"],
            "Complaint": ["complaint", "issue", "problem", "unsatisfied"],
        }
        
        # Category priority order for ties
        self.category_priority = ["Complaint", "Critique", "Feedback", "Positive Response", "Other"]
    
    def parse_input(self, data_input, format_type):
        """Parse and validate input data"""
        records = []
        errors = []
        
        try:
            if format_type == "csv":
                csv_reader = csv.DictReader(StringIO(data_input))
                records = list(csv_reader)
            elif format_type == "json":
                data = json.loads(data_input)
                records = data.get("conversations", [])
            else:
                return [], ["ERROR: Invalid data format. Please provide data in CSV or JSON format."]
        except Exception as e:
            return [], [f"ERROR: Failed to parse input data. {str(e)}"]
        
        # Validate records
        for i, record in enumerate(records):
            # Check for required fields
            missing_fields = []
            for field in ["conversation_id", "sender", "timestamp", "message"]:
                if field not in record or not record[field]:
                    if field == "message":
                        errors.append(f"ERROR: 'message' field cannot be empty in row {i+1}.")
                    else:
                        missing_fields.append(field)
            
            if missing_fields:
                errors.append(f"ERROR: Missing required field(s): {', '.join(missing_fields)} in row {i+1}.")
        
        return records, errors
    
    def validate_data(self, records):
        """Generate data validation report"""
        validation_report = "# Data Validation Report\n"
        validation_report += "## 1. Data Structure Check:\n"
        
        # Group records by conversation_id
        conversations = {}
        for record in records:
            conversation_id = record["conversation_id"]
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            conversations[conversation_id].append(record)
        
        validation_report += f"- Total conversations processed: {len(conversations)}\n"
        validation_report += f"- Total fields per record: 4\n\n"
        
        validation_report += "## 2. Required Fields Check:\n"
        validation_report += "- conversation_id: present\n"
        validation_report += "- sender: present\n"
        validation_report += "- timestamp: present\n"
        validation_report += "- message: present\n\n"
        
        validation_report += "## 3. Data Content Validation:\n"
        validation_report += "- \"message\" field not empty: validated\n\n"
        
        validation_report += "Validation Summary:\n"
        validation_report += "Data validation is successful! Proceeding with analysis...\n\n"
        
        return validation_report, conversations
    
    def calculate_conversation_metrics(self, messages):
        """Calculate metrics for a conversation"""
        total_messages = len(messages)
        total_words = sum(len(msg["message"].split()) for msg in messages)
        avg_words = round(total_words / total_messages, 2) if total_messages > 0 else 0
        conversation_detail = "Detailed" if avg_words >= 20 else "Brief"
        
        return {
            "total_messages": total_messages,
            "total_words": total_words,
            "avg_words": avg_words,
            "conversation_detail": conversation_detail
        }
    
    def calculate_sentiment(self, messages):
        """Calculate sentiment scores for a conversation"""
        all_text = " ".join(msg["message"].lower() for msg in messages)
        
        positive_count = sum(all_text.count(word) for word in self.positive_words)
        negative_count = sum(all_text.count(word) for word in self.negative_words)
        
        sentiment_score = positive_count - negative_count
        
        if sentiment_score > 0:
            sentiment_category = "Positive"
        elif sentiment_score < 0:
            sentiment_category = "Negative"
        else:
            sentiment_category = "Neutral"
        
        return {
            "positive_count": positive_count,
            "negative_count": negative_count,
            "sentiment_score": sentiment_score,
            "sentiment_category": sentiment_category
        }
    
    def categorize_chat(self, messages):
        """Categorize chat based on keywords"""
        categories = {cat: 0 for cat in list(self.category_keywords.keys()) + ["Other"]}
        
        for msg in messages:
            message_text = msg["message"].lower()
            categorized = False
            
            for category, keywords in self.category_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in message_text:
                        categories[category] += 1
                        categorized = True
                        break
                if categorized:
                    break
            
            if not categorized:
                categories["Other"] += 1
        
        # Determine dominant category
        max_count = max(categories.values())
        dominant_categories = [cat for cat, count in categories.items() if count == max_count]
        
        if len(dominant_categories) == 1:
            dominant_category = dominant_categories[0]
        else:
            # Use priority order for tie-breaking
            for category in self.category_priority:
                if category in dominant_categories:
                    dominant_category = category
                    break
        
        # Generate recommendation based on dominant category
        recommendations = {
            "Complaint": "This conversation primarily consists of complaints. It is advised to immediately reach out to the customer, investigate the issue in detail, and provide prompt resolution and compensation if appropriate to restore satisfaction.",
            "Critique": "This conversation mainly contains critiques. It is recommended to acknowledge the customer's concerns, express understanding, and communicate a clear plan of action to address and improve upon the issues raised.",
            "Feedback": "This conversation is driven by customer feedback. It is suggested to thank the customer for their input, ensure that their suggestions are noted, and invite them to provide further insights to help improve services.",
            "Positive Response": "This conversation reflects a positive customer sentiment. It is recommended to encourage the customer to share their positive experience publicly and maintain this level of service.",
            "Other": "This conversation does not clearly fall into a specific category. Standard customer service follow-up is advised to ensure that all customer queries are addressed appropriately."
        }
        
        return {
            "category_counts": categories,
            "dominant_category": dominant_category,
            "recommendation": recommendations[dominant_category]
        }
    
    def analyze_conversations(self, conversations):
        """Analyze all conversations and generate report"""
        formulas_section = "# Formulas Used:\n"
        formulas_section += "1. Average Words per Message:\n"
        formulas_section += "   $$ \\text{Average Words} = \\frac{\\text{Total Words}}{\\text{Total Messages}} $$\n"
        formulas_section += "2. Sentiment Score:\n"
        formulas_section += "   $$ \\text{Sentiment Score} = \\text{(Count of Positive Words)} - \\text{(Count of Negative Words)} $$\n\n"
        
        summary_section = "# Conversation Analysis Summary:\n"
        summary_section += f"- Total Conversations Evaluated: {len(conversations)}\n\n"
        
        detailed_section = "# Detailed Analysis for Each Conversation:\n"
        
        for conv_id, messages in conversations.items():
            # Calculate metrics
            metrics = self.calculate_conversation_metrics(messages)
            sentiment = self.calculate_sentiment(messages)
            categorization = self.categorize_chat(messages)
            
            detailed_section += f"## Conversation ID: {conv_id}\n\n"
            
            # Input Data Summary
            detailed_section += "### Input Data Summary:\n"
            detailed_section += f"- Total Messages: {metrics['total_messages']}\n"
            detailed_section += f"- Total Words: {metrics['total_words']}\n"
            detailed_section += f"- Average Words per Message: {metrics['avg_words']} words\n\n"
            
            # Step-by-Step Calculations
            detailed_section += "### Step-by-Step Calculations:\n"
            detailed_section += "1. **Calculate Total Messages:**\n"
            detailed_section += f"   - Count of messages in conversation: {metrics['total_messages']}\n\n"
            
            detailed_section += "2. **Calculate Total Words:**\n"
            detailed_section += "   - Words from each message:\n"
            for i, msg in enumerate(messages):
                word_count = len(msg["message"].split())
                detailed_section += f"     - Message {i+1}: {word_count} words\n"
            detailed_section += f"   - Sum of all word counts: {metrics['total_words']} words\n\n"
            
            detailed_section += "3. **Calculate the Average Words per Message:**\n"
            detailed_section += f"   - Average Words = Total Words / Total Messages\n"
            detailed_section += f"   - Average Words = {metrics['total_words']} / {metrics['total_messages']} = {metrics['avg_words']} words\n\n"
            
            detailed_section += "4. **Determine Conversation Detail Level:**\n"
            detailed_section += f"   - IF Average Words ({metrics['avg_words']}) ≥ 20, THEN \"Detailed\"\n"
            detailed_section += f"   - ELSE \"Brief\"\n"
            detailed_section += f"   - Result: Conversation is \"{metrics['conversation_detail']}\"\n\n"
            
            detailed_section += "5. **Sentiment Analysis:**\n"
            detailed_section += "   - Count of positive words in all messages:\n"
            detailed_section += f"     - Words checked: {', '.join(self.positive_words)}\n"
            detailed_section += f"     - Count: {sentiment['positive_count']}\n"
            detailed_section += "   - Count of negative words in all messages:\n"
            detailed_section += f"     - Words checked: {', '.join(self.negative_words)}\n"
            detailed_section += f"     - Count: {sentiment['negative_count']}\n"
            detailed_section += "   - Sentiment Score calculation:\n"
            detailed_section += f"     - Sentiment Score = Positive Words Count - Negative Words Count\n"
            detailed_section += f"     - Sentiment Score = {sentiment['positive_count']} - {sentiment['negative_count']} = {sentiment['sentiment_score']}\n"
            detailed_section += "   - Sentiment categorization:\n"
            detailed_section += f"     - IF Score ({sentiment['sentiment_score']}) > 0, THEN \"Positive\"\n"
            detailed_section += f"     - ELSE IF Score ({sentiment['sentiment_score']}) < 0, THEN \"Negative\"\n"
            detailed_section += f"     - ELSE \"Neutral\"\n"
            detailed_section += f"     - Result: Sentiment is \"{sentiment['sentiment_category']}\"\n\n"
            
            detailed_section += "6. **Chat Categorization:**\n"
            detailed_section += "   - Keyword counts for each category:\n"
            for category, count in categorization["category_counts"].items():
                if category != "Other":
                    keywords = self.category_keywords[category]
                    detailed_section += f"     - {category}: {count} (Keywords: {', '.join(keywords)})\n"
                else:
                    detailed_section += f"     - {category}: {count} (No specific keywords matched)\n"
            
            detailed_section += "   - Determining dominant category:\n"
            if len([cat for cat, count in categorization["category_counts"].items() if count == max(categorization["category_counts"].values())]) == 1:
                detailed_section += f"     - Category with highest count: {categorization['dominant_category']}\n"
            else:
                detailed_section += "     - Multiple categories tied with highest count\n"
                detailed_section += f"     - Using priority order: Complaint > Critique > Feedback > Positive Response > Other\n"
                detailed_section += f"     - Highest priority category among ties: {categorization['dominant_category']}\n"
            
            detailed_section += "\n7. **Customer Service Enhancement Recommendation:**\n"
            detailed_section += f"   - Based on dominant category \"{categorization['dominant_category']}\"\n"
            detailed_section += f"   - Recommendation: {categorization['recommendation']}\n\n"
            
            # Final Summary
            detailed_section += "### Final Summary:\n"
            detailed_section += f"- Conversation Detail: {metrics['conversation_detail']}\n"
            detailed_section += f"- Sentiment Category: {sentiment['sentiment_category']}\n"
            detailed_section += f"- Dominant Chat Category: {categorization['dominant_category']}\n"
            detailed_section += f"- Service Recommendation: {categorization['recommendation']}\n\n"
        
        feedback_request = "# Feedback Request\n\n"
        feedback_request += "Would you like detailed calculations for any specific conversation? Please rate this analysis on a scale of 1-5.\n"
        
        return formulas_section + summary_section + detailed_section + feedback_request
    
    def process_data(self, data_input, format_type):
        """Process input data and generate full report"""
        records, errors = self.parse_input(data_input, format_type)
        
        if errors:
            return "\n".join(errors)
        
        validation_report, conversations = self.validate_data(records)
        analysis_report = self.analyze_conversations(conversations)
        
        return validation_report + analysis_report
    
    def greeting(self, message):
        """Generate appropriate greeting based on user message"""
        message_lower = message.lower()
        
        # Check for urgency keywords
        if any(word in message_lower for word in ["urgent", "asap", "emergency"]):
            return "ChatLogSummarizer-AI here! Let's quickly analyze your chat logs."
        
        # Extract name if provided
        name_match = re.search(r"my name is (\w+)", message_lower)
        if name_match:
            name = name_match.group(1)
            return f"Hello, {name}! I'm ChatLogSummarizer-AI, here to assist you with your chat log analysis."
        
        # Check for mood keywords
        if any(word in message_lower for word in ["happy", "excited", "joyful", "great"]):
            return "Hello! It's great to see your positive tone. I'm here to help summarize your chat logs!"
        
        if any(word in message_lower for word in ["sad", "down", "unhappy"]):
            return "Hello. I'm sorry you're feeling down. Let's work together to analyze your chat logs for insights."
        
        if any(word in message_lower for word in ["angry", "frustrated", "mad"]):
            return "Hello. I understand you're frustrated. Let's carefully review your chat logs for actionable insights."
        
        # Default greeting
        return "Greetings! I am ChatLogSummarizer-AI, your assistant for categorizing and summarizing chat/email logs. Please share your chat log data in CSV or JSON format to begin."

# Example usage
def main():
    summarizer = ChatLogSummarizer()
    # # Example data
    # example_csv = """conversation_id,sender,timestamp,message
    # conv1,customer,01-02-2023,"Hello, I have a problem with my order."
    # conv1,agent,01-02-2023,"I'm sorry to hear that. What seems to be the issue?"
    # conv1,customer,01-02-2023,"The product arrived damaged. I'm very unhappy with this."
    # conv1,agent,01-02-2023,"I apologize for the inconvenience. We'll send a replacement right away."
    # conv2,customer,02-02-2023,"Thank you for the excellent service! I'm very happy with my purchase."
    # conv2,agent,02-02-2023,"You're welcome! We're glad you had a great experience."
    # """
    # # Process CSV data
    # print("=== CSV Data Analysis ===")
    # csv_report = summarizer.process_data(example_csv, "csv")
    # print(csv_report)
    
    example_json = """{
    "conversations": [
        {
        "conversation_id": "conv100",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "I need help with my account."
        },
        {
        "conversation_id": "conv100",
        "sender": "agent",
        "timestamp": "12-03-2021",
        "message": "Sure, I can help you with your account details."
        },
        {
        "conversation_id": "conv100",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "I forgot my password and cannot log in."
        },
        {
        "conversation_id": "conv100",
        "sender": "agent",
        "timestamp": "12-03-2021",
        "message": "Please try resetting your password using the 'Forgot Password' link."
        },
        {
        "conversation_id": "conv100",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "I will try that, thank you."
        },
        {
        "conversation_id": "conv101",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "I recently updated the software and noticed several performance issues, including slow loading times and frequent crashes that disrupt my workflow significantly."
        },
        {
        "conversation_id": "conv101",
        "sender": "agent",
        "timestamp": "12-03-2021",
        "message": "We apologize for the inconvenience caused by the update; our technical team is actively investigating these performance issues and working on a patch to enhance stability and speed."
        },
        {
        "conversation_id": "conv101",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "The update not only affected performance but also changed the interface drastically, making it difficult to navigate, which has impacted my overall user experience."
        },
        {
        "conversation_id": "conv101",
        "sender": "agent",
        "timestamp": "12-03-2021",
        "message": "Thank you for your detailed feedback; we are documenting your concerns and will prioritize improvements in our next update to ensure a better user experience."
        },
        {
        "conversation_id": "conv101",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "I appreciate the prompt response and detailed explanation regarding the ongoing efforts to resolve these issues."
        },
        {
        "conversation_id": "conv102",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "I am very satisfied with the recent improvements in the service quality and customer support."
        },
        {
        "conversation_id": "conv102",
        "sender": "agent",
        "timestamp": "12-03-2021",
        "message": "Thank you for your positive feedback; we are glad you enjoy the new design and improved features."
        },
        {
        "conversation_id": "conv102",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "The new features have improved navigation and overall functionality remarkably."
        },
        {
        "conversation_id": "conv102",
        "sender": "agent",
        "timestamp": "12-03-2021",
        "message": "We appreciate your kind words and are committed to further enhancing our service."
        },
        {
        "conversation_id": "conv102",
        "sender": "customer",
        "timestamp": "12-03-2021",
        "message": "Please keep up the great work and continue to listen to your customers."
        }
    ]
    }
"""
    
    print("\n\n=== JSON Data Analysis ===")
    json_report = summarizer.process_data(example_json, "json")
    print(json_report)

if __name__ == "__main__":
    main()
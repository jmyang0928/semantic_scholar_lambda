import json
import requests
from semanticscholar import SemanticScholar
from semanticscholar.Paper import Paper

def lambda_handler(event, context):
    """
    一個強化的 AWS Lambda 函式，用於查詢論文引用次數與作者 H-index。
    包含了詳細的日誌記錄與網路連線診斷功能。
    """
    print(f"Received event: {json.dumps(event)}")

    title = None
    
    # --- 步驟 A: 從各種可能的事件來源中提取 'title' ---
    # 1. 優先嘗試直接從 event 的頂層獲取 (用於 Lambda 主控台的簡單測試)
    if isinstance(event, dict) and 'title' in event:
        title = event.get('title')

    # 2. 如果沒有，再檢查是否為 API Gateway 事件
    if not title and isinstance(event, dict):
        # 處理 POST 請求的 body
        body = {}
        if 'body' in event and event.get('body'):
            try:
                # API Gateway 的 body 是 string，需要 parse
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                print("Warning: Could not parse event body as JSON.")
                pass
        
        # 檢查 GET 參數 (queryStringParameters) 或剛才解析完的 POST body
        title = event.get('queryStringParameters', {}).get('title') or body.get('title')

    if not title:
        print("Error: 'title' not found in event.")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "請求格式錯誤，請在請求中提供論文標題 'title'。"}, ensure_ascii=False)
        }

    print(f"成功提取到查詢標題: '{title}'")

    try:
        # --- 步驟 B: 網路連線診斷 ---
        print("步驟 1: 測試對 google.com 的基本連線...")
        try:
            response = requests.get("https://www.google.com", timeout=10)
            print(f"步驟 1: 成功。狀態碼: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"步驟 1: 失敗！無法連線到 google.com。錯誤: {e}")
            raise Exception("無法建立對外網路連線。請檢查 VPC、子網路及 NAT Gateway 設定。")

        # --- 步驟 C: 執行主要應用程式邏輯 ---
        print("步驟 2: 初始化 SemanticScholar client...")
        sch = SemanticScholar(timeout=30)
        print("步驟 2: Client 初始化成功。")

        print(f"步驟 3: 正在搜尋論文 '{title}'...")
        search_results = sch.search_paper(title, limit=1, fields=["title", "paperId", "citationCount", "authors"])
        print("步驟 3: 論文搜尋完成。")

        if not search_results:
            print("步驟 4: 找不到論文，準備回傳 404 Not Found。")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"找不到標題為 '{title}' 的論文。"}, ensure_ascii=False)
            }
        
        paper: Paper = search_results[0]
        print(f"步驟 4: 找到論文 '{paper.title}'，引用次數: {paper.citationCount}。")

        author_ids = [a.authorId for a in paper.authors if a.authorId]
        if not author_ids:
            print("步驟 5: 論文沒有可查詢的作者 ID。")
            authors_details = []
        else:
            print(f"步驟 5: 正在查詢 {len(author_ids)} 位作者的 h-index...")
            authors_details = sch.get_authors(author_ids, fields=["name", "hIndex"])
            print("步驟 5: 作者查詢完成。")

        author_info = [
            {'name': a.name, 'hIndex': a.hIndex} for a in authors_details
        ]

        result = {
            'paperTitle': paper.title,
            'citationCount': paper.citationCount,
            'authors': author_info
        }

        print("步驟 6: 處理完成，準備回傳成功結果。")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result, ensure_ascii=False)
        }

    except Exception as e:
        # 捕獲所有可能的錯誤 (網路、API、程式邏輯等)
        print(f"函式在執行過程中發生嚴重錯誤: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"處理請求時發生內部錯誤: {str(e)}"}, ensure_ascii=False)
        }
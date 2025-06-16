import json
from semanticscholar import SemanticScholar
from semanticscholar.Paper import Paper # 用於 type hint，可選

def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    :param event: API Gateway event, 包含 'queryStringParameters' 或 body，其中應有 'title' 欄位
    :param context: Lambda a執行環境資訊
    :return: 包含論文資訊的 JSON 格式 response
    """
    # 從 event 中獲取論文標題，支援 GET (queryStringParameters) 或 POST (body)
    # 例如： {"title": "yolov7"}
    print(f"Received event: {event}")
    
    body = {}
    if 'body' in event and event['body']:
        body = json.loads(event['body'])
        
    title = event.get('queryStringParameters', {}).get('title') or body.get('title')

    if not title:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "請在請求中提供論文標題 'title'。"})
        }

    try:
        sch = SemanticScholar(timeout=30)
        
        # 搜尋論文
        search_results = sch.search_paper(title, limit=1, fields=["title", "paperId", "citationCount", "authors"])
        
        if not search_results:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"找不到標題為 '{title}' 的論文。"})
            }
            
        paper: Paper = search_results[0]

        # 批次查詢作者 h-index
        author_ids = [a.authorId for a in paper.authors if a.authorId]
        authors_details = sch.get_authors(author_ids, fields=["name", "hIndex"])
        
        author_info = [
            {'name': a.name, 'hIndex': a.hIndex} for a in authors_details
        ]

        # 準備回傳結果
        result = {
            'paperTitle': paper.title,
            'citationCount': paper.citationCount,
            'authors': author_info
        }

        # 成功的回應
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result, ensure_ascii=False) # ensure_ascii=False 確保中文正常顯示
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"處理請求時發生內部錯誤: {str(e)}"})
        }
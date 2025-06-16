import json
from semanticscholar import SemanticScholar
from semanticscholar.Paper import Paper

def lambda_handler(event, context):
    """
    一個優化後的 AWS Lambda 函式，用於查詢論文引用次數與作者 H-index。
    """
    # 從各種可能的事件來源中提取 'title'
    title = None
    if isinstance(event, dict) and 'title' in event:
        title = event.get('title')

    if not title and isinstance(event, dict):
        body = {}
        if 'body' in event and event.get('body'):
            try:
                body = json.loads(event['body'])
            except (json.JSONDecodeError, TypeError):
                pass
        
        title = event.get('queryStringParameters', {}).get('title') or body.get('title')

    if not title:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "請求格式錯誤，請在請求中提供論文標題 'title'。"}, ensure_ascii=False)
        }

    try:
        # 執行主要應用程式邏輯
        sch = SemanticScholar(timeout=95) # 給予一個略長於90秒的超時
        
        search_results = sch.search_paper(title, limit=1, fields=["title", "paperId", "citationCount", "authors"])

        if not search_results:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f"找不到標題為 '{title}' 的論文。"}, ensure_ascii=False)
            }
        
        paper: Paper = search_results[0]

        author_ids = [a.authorId for a in paper.authors if a.authorId]
        
        authors_details = []
        if author_ids:
            authors_details = sch.get_authors(author_ids, fields=["name", "hIndex"])

        author_info = [
            {'name': a.name, 'hIndex': a.hIndex} for a in authors_details
        ]

        result = {
            'paperTitle': paper.title,
            'citationCount': paper.citationCount,
            'authors': author_info
        }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(result, ensure_ascii=False)
        }

    except Exception as e:
        # 在發生錯誤時，仍然保留日誌記錄，這對於維護至關重要
        print(f"An error occurred while processing title '{title}'. Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"處理請求時發生內部錯誤: {str(e)}"}, ensure_ascii=False)
        }
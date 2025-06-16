# Semantic Scholar Lambda Service

A serverless application built on AWS Lambda that queries academic paper information through the Semantic Scholar API, including paper titles, citation counts, and authors' h-index metrics.

## Features

- 🔍 **Paper Search**: Search academic papers by title
- 📊 **Citation Statistics**: Retrieve paper citation counts
- 👥 **Author Information**: Query authors' h-index metrics
- 🚀 **Serverless Architecture**: High availability and auto-scaling with AWS Lambda
- 🌐 **RESTful API**: HTTP interface through API Gateway

## Project Structure

```
semantic_scholar_lambda/
├── src/
│   ├── lambda_function.py    # Main Lambda function
│   └── requirements.txt      # Python dependencies
├── template.yaml            # AWS SAM deployment template
└── README.md               # Project documentation
```

## Technology Stack

- **Runtime**: Python 3.9
- **Main Package**: `semanticscholar` Python SDK
- **Cloud Services**: AWS Lambda + API Gateway
- **Deployment Tool**: AWS SAM (Serverless Application Model)

## Installation & Setup

### Prerequisites

1. [AWS CLI](https://aws.amazon.com/cli/) installed and configured
2. [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed
3. Python 3.9 or higher

### Local Development Setup

1. Clone the project locally:
```bash
git clone <repository-url>
cd semantic_scholar_lambda
```

2. Install Python dependencies:
```bash
pip install -r src/requirements.txt
```

3. Test Lambda function locally:
```bash
sam local start-api
```

## Deployment Guide

### Deploy with AWS SAM

1. Build the application:
```bash
sam build
```

2. Deploy to AWS:
```bash
sam deploy --guided
```

Use the `--guided` parameter for first-time deployment to configure deployment parameters.

3. Subsequent deployments:
```bash
sam deploy
```

## API Usage

### Endpoint Information

- **URL**: `https://{api-id}.execute-api.{region}.amazonaws.com/Prod/paper`
- **Method**: GET
- **Parameter**: `title` (paper title)

### Request Examples

#### GET Request
```bash
curl "https://your-api-endpoint.amazonaws.com/Prod/paper?title=yolov7"
```

#### POST Request
```bash
curl -X POST \
  https://your-api-endpoint.amazonaws.com/Prod/paper \
  -H 'Content-Type: application/json' \
  -d '{"title": "yolov7"}'
```

### Response Format

#### Success Response (200)
```json
{
  "paperTitle": "YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors",
  "citationCount": 1250,
  "authors": [
    {
      "name": "Chien-Yao Wang",
      "hIndex": 25
    },
    {
      "name": "Alexey Bochkovskiy",
      "hIndex": 18
    }
  ]
}
```

#### Error Responses

**400 - Missing Parameter**
```json
{
  "error": "Please provide paper title 'title' in the request."
}
```

**404 - Paper Not Found**
```json
{
  "error": "No paper found with title 'your-title'."
}
```

**500 - Internal Error**
```json
{
  "error": "Internal error occurred while processing request: {detailed error message}"
}
```

## Configuration

### Lambda Function Settings

- **Runtime**: Python 3.9
- **Memory**: 256 MB
- **Timeout**: 90 seconds
- **Handler**: lambda_function.lambda_handler

### API Gateway Settings

- **Path**: `/paper`
- **Supported Methods**: GET, POST
- **Content Type**: application/json

## Monitoring & Debugging

### CloudWatch Logs

Lambda function execution logs are automatically recorded to CloudWatch. You can view them in the AWS Console:

1. Go to CloudWatch service
2. Select "Log groups"
3. Find `/aws/lambda/PaperLookupFunction`

### Common Issue Solutions

1. **Timeout Errors**: Increase Lambda function timeout
2. **Out of Memory**: Adjust MemorySize setting
3. **API Limits**: Semantic Scholar API has usage limits, control request frequency appropriately

## Local Testing

### Testing Lambda Function

Create test event file `test-event.json`:

```json
{
  "queryStringParameters": {
    "title": "transformer"
  }
}
```

Run local test:
```bash
sam local invoke PaperLookupFunction -e test-event.json
```

### Local API Testing

Start local API:
```bash
sam local start-api
```

Test request:
```bash
curl "http://localhost:3000/paper?title=transformer"
```

## Cost Estimation

- **Lambda Request Fee**: $0.20 per million requests
- **Lambda Compute Fee**: Based on memory and execution time
- **API Gateway**: $3.50 per million API calls

Under normal usage, monthly costs typically range from $1-10.

## Security Considerations

- Use IAM roles to manage Lambda permissions
- API Gateway can be configured with API keys or OAuth authentication
- Recommended to set up CloudWatch alarms for monitoring abnormal usage

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contributing

Issues and Pull Requests are welcome!

1. Fork this project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## Contact

For any questions or suggestions, please contact via GitHub Issues.

---

**Note**: This service depends on the Semantic Scholar API. Please comply with their terms of use and limitations.

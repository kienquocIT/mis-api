# API Documentation - Bflow Workflow Management System
**Version:** 1.0  
**Date:** 2025-07-25  
**Author:** BA / Technical Lead  
**Status:** Draft

## 1. API Overview

### 1.1 Base Information
- **Base URL Production**: `https://api.bflow.com/api/v1`
- **Base URL Staging**: `https://staging-api.bflow.com/api/v1`
- **Protocol**: HTTPS only
- **Data Format**: JSON
- **API Version**: v1
- **Rate Limiting**: 1000 requests per hour per API key

### 1.2 Authentication
All API requests require authentication using JWT tokens.

```http
Authorization: Bearer <your-jwt-token>
```

### 1.3 Common Headers
```http
Content-Type: application/json
Accept: application/json
X-Tenant-ID: <tenant-uuid>
X-Request-ID: <unique-request-id>
```

### 1.4 Response Format
```json
{
    "success": true,
    "data": {
        // Response data
    },
    "meta": {
        "timestamp": "2025-07-25T10:00:00Z",
        "request_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "errors": []
}
```

### 1.5 Error Response Format
```json
{
    "success": false,
    "data": null,
    "meta": {
        "timestamp": "2025-07-25T10:00:00Z",
        "request_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "errors": [
        {
            "code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "field": "name",
            "details": "Name is required"
        }
    ]
}
```

### 1.6 HTTP Status Codes
| Status Code | Description |
|------------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request succeeded with no response body |
| 400 | Bad Request - Invalid request format |
| 401 | Unauthorized - Authentication failed |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource conflict |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

## 2. Authentication Endpoints

### 2.1 Login
**Endpoint:** `POST /auth/login`  
**Description:** Authenticate user and obtain JWT tokens

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "securepassword",
    "company_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "user@example.com",
            "full_name": "John Doe",
            "role": "workflow_designer"
        }
    }
}
```

### 2.2 Refresh Token
**Endpoint:** `POST /auth/refresh`  
**Description:** Refresh access token using refresh token

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2.3 Logout
**Endpoint:** `POST /auth/logout`  
**Description:** Invalidate current tokens

**Headers Required:** `Authorization: Bearer <token>`

## 3. Workflow Configuration API

### 3.1 List Workflows
**Endpoint:** `GET /workflows`  
**Description:** Retrieve list of workflows with filtering and pagination

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| app_id | UUID | No | Filter by application |
| is_active | boolean | No | Filter by active status |
| is_applied | boolean | No | Filter by applied status |
| search | string | No | Search in name and description |
| page | integer | No | Page number (default: 1) |
| page_size | integer | No | Items per page (default: 20, max: 100) |
| order_by | string | No | Sort field (name, created_at, updated_at) |
| order_dir | string | No | Sort direction (asc, desc) |

**Response:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Leave Request Approval",
                "description": "Workflow for leave request approval process",
                "app": {
                    "id": "660e8400-e29b-41d4-a716-446655440000",
                    "name": "E-Office",
                    "code": "eoffice"
                },
                "is_active": true,
                "is_applied": true,
                "is_multi_company": false,
                "node_count": 5,
                "created_at": "2025-07-01T10:00:00Z",
                "updated_at": "2025-07-20T15:30:00Z"
            }
        ],
        "pagination": {
            "total": 25,
            "page": 1,
            "page_size": 20,
            "total_pages": 2,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

### 3.2 Get Workflow Details
**Endpoint:** `GET /workflows/{workflow_id}`  
**Description:** Retrieve detailed workflow configuration including nodes and associations

**Path Parameters:**
- `workflow_id` (UUID, required): Workflow identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Leave Request Approval",
        "description": "Workflow for leave request approval process",
        "app": {
            "id": "660e8400-e29b-41d4-a716-446655440000",
            "name": "E-Office",
            "code": "eoffice"
        },
        "is_active": true,
        "is_applied": true,
        "is_multi_company": false,
        "zones": [
            {
                "id": 1,
                "name": "Employee Information",
                "is_editable": false,
                "is_viewable": true
            },
            {
                "id": 2,
                "name": "Leave Details",
                "is_editable": true,
                "is_viewable": true
            }
        ],
        "nodes": [
            {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "name": "Start",
                "action": 0,
                "is_initial": true,
                "is_end": false,
                "collaborator_option": {
                    "type": "creator",
                    "zones": [1, 2]
                },
                "coordinate": {
                    "x": 100,
                    "y": 100
                }
            },
            {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "name": "Manager Approval",
                "action": 1,
                "is_initial": false,
                "is_end": false,
                "collaborator_option": {
                    "type": "in_workflow",
                    "position": "direct_manager",
                    "zones": [2]
                }
            }
        ],
        "associations": [
            {
                "id": "990e8400-e29b-41d4-a716-446655440000",
                "source_node_id": "770e8400-e29b-41d4-a716-446655440000",
                "dest_node_id": "880e8400-e29b-41d4-a716-446655440000",
                "condition": null
            }
        ],
        "created_at": "2025-07-01T10:00:00Z",
        "updated_at": "2025-07-20T15:30:00Z",
        "created_by": {
            "id": "aa0e8400-e29b-41d4-a716-446655440000",
            "full_name": "Admin User"
        }
    }
}
```

### 3.3 Create Workflow
**Endpoint:** `POST /workflows`  
**Description:** Create a new workflow configuration

**Request Body:**
```json
{
    "name": "Purchase Order Approval",
    "description": "Workflow for purchase order approval based on amount",
    "app_id": "660e8400-e29b-41d4-a716-446655440000",
    "is_multi_company": false,
    "zones": [
        {
            "name": "Order Information",
            "is_editable": false,
            "is_viewable": true
        },
        {
            "name": "Approval Section",
            "is_editable": true,
            "is_viewable": true
        }
    ],
    "nodes": [
        {
            "name": "Start",
            "action": 0,
            "is_initial": true,
            "collaborator_option": {
                "type": "creator"
            },
            "coordinate": {"x": 100, "y": 100}
        },
        {
            "name": "Manager Review",
            "action": 1,
            "collaborator_option": {
                "type": "out_form",
                "employee_ids": ["aa0e8400-e29b-41d4-a716-446655440000"]
            },
            "coordinate": {"x": 300, "y": 100}
        }
    ],
    "associations": [
        {
            "source_node_name": "Start",
            "dest_node_name": "Manager Review",
            "condition": {
                "field": "total_amount",
                "operator": "less_than",
                "value": 10000
            }
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "bb0e8400-e29b-41d4-a716-446655440000",
        "name": "Purchase Order Approval",
        "status": "draft",
        "message": "Workflow created successfully"
    }
}
```

### 3.4 Update Workflow
**Endpoint:** `PUT /workflows/{workflow_id}`  
**Description:** Update existing workflow configuration

**Path Parameters:**
- `workflow_id` (UUID, required): Workflow identifier

**Request Body:** Same structure as Create Workflow

**Note:** Cannot update workflow if it's currently applied and has active instances

### 3.5 Delete Workflow
**Endpoint:** `DELETE /workflows/{workflow_id}`  
**Description:** Delete workflow (soft delete)

**Path Parameters:**
- `workflow_id` (UUID, required): Workflow identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "message": "Workflow deleted successfully"
    }
}
```

### 3.6 Apply Workflow
**Endpoint:** `POST /workflows/{workflow_id}/apply`  
**Description:** Apply workflow to make it active for use

**Path Parameters:**
- `workflow_id` (UUID, required): Workflow identifier

**Request Body:**
```json
{
    "effective_date": "2025-08-01T00:00:00Z",
    "notify_users": true
}
```

### 3.7 Export Workflow
**Endpoint:** `GET /workflows/{workflow_id}/export`  
**Description:** Export workflow configuration

**Path Parameters:**
- `workflow_id` (UUID, required): Workflow identifier

**Query Parameters:**
- `format` (string): Export format (json, bpmn2, xml)

**Response:** File download with appropriate content type

### 3.8 Import Workflow
**Endpoint:** `POST /workflows/import`  
**Description:** Import workflow from file

**Request Body (multipart/form-data):**
- `file`: Workflow definition file
- `format`: Import format (json, bpmn2, xml)
- `name`: Override workflow name (optional)

## 4. Workflow Runtime API

### 4.1 Execute Workflow
**Endpoint:** `POST /runtime/execute`  
**Description:** Start workflow execution on a document

**Request Body:**
```json
{
    "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_type": "leave_request",
    "document_id": "cc0e8400-e29b-41d4-a716-446655440000",
    "initial_data": {
        "priority": "high",
        "notes": "Urgent family matter"
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "runtime_id": "dd0e8400-e29b-41d4-a716-446655440000",
        "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
        "document_id": "cc0e8400-e29b-41d4-a716-446655440000",
        "status": "in_progress",
        "current_stage": {
            "id": "ee0e8400-e29b-41d4-a716-446655440000",
            "name": "Manager Approval",
            "assignees": [
                {
                    "id": "ff0e8400-e29b-41d4-a716-446655440000",
                    "user": {
                        "id": "aa0e8400-e29b-41d4-a716-446655440000",
                        "full_name": "John Manager"
                    },
                    "assigned_at": "2025-07-25T10:00:00Z"
                }
            ]
        },
        "created_at": "2025-07-25T10:00:00Z"
    }
}
```

### 4.2 Get Runtime Status
**Endpoint:** `GET /runtime/{runtime_id}`  
**Description:** Get current status of workflow execution

**Path Parameters:**
- `runtime_id` (UUID, required): Runtime instance identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "dd0e8400-e29b-41d4-a716-446655440000",
        "workflow": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Leave Request Approval"
        },
        "document": {
            "type": "leave_request",
            "id": "cc0e8400-e29b-41d4-a716-446655440000",
            "title": "Leave Request - John Doe"
        },
        "status": "in_progress",
        "stages": [
            {
                "id": "110e8400-e29b-41d4-a716-446655440000",
                "node_name": "Start",
                "status": "completed",
                "started_at": "2025-07-25T10:00:00Z",
                "completed_at": "2025-07-25T10:01:00Z",
                "completed_by": {
                    "id": "220e8400-e29b-41d4-a716-446655440000",
                    "full_name": "John Doe"
                }
            },
            {
                "id": "ee0e8400-e29b-41d4-a716-446655440000",
                "node_name": "Manager Approval",
                "status": "in_progress",
                "started_at": "2025-07-25T10:01:00Z",
                "assignees": [
                    {
                        "id": "ff0e8400-e29b-41d4-a716-446655440000",
                        "user": {
                            "id": "aa0e8400-e29b-41d4-a716-446655440000",
                            "full_name": "John Manager"
                        },
                        "status": "pending",
                        "zones": [2]
                    }
                ]
            }
        ],
        "created_at": "2025-07-25T10:00:00Z",
        "updated_at": "2025-07-25T10:01:00Z"
    }
}
```

### 4.3 Get Runtime Diagram
**Endpoint:** `GET /runtime/{runtime_id}/diagram`  
**Description:** Get visual representation of workflow progress

**Path Parameters:**
- `runtime_id` (UUID, required): Runtime instance identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "nodes": [
            {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "name": "Start",
                "status": "completed",
                "coordinate": {"x": 100, "y": 100}
            },
            {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "name": "Manager Approval",
                "status": "active",
                "coordinate": {"x": 300, "y": 100}
            }
        ],
        "edges": [
            {
                "source": "770e8400-e29b-41d4-a716-446655440000",
                "target": "880e8400-e29b-41d4-a716-446655440000",
                "status": "completed"
            }
        ],
        "current_position": "880e8400-e29b-41d4-a716-446655440000"
    }
}
```

### 4.4 List User Tasks
**Endpoint:** `GET /tasks`  
**Description:** Get tasks assigned to current user

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by status (pending, completed, all) |
| priority | string | No | Filter by priority (low, medium, high, urgent) |
| workflow_id | UUID | No | Filter by workflow |
| document_type | string | No | Filter by document type |
| assigned_from | date | No | Filter by assignment date (from) |
| assigned_to | date | No | Filter by assignment date (to) |
| search | string | No | Search in document title |
| page | integer | No | Page number |
| page_size | integer | No | Items per page |

**Response:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "ff0e8400-e29b-41d4-a716-446655440000",
                "runtime": {
                    "id": "dd0e8400-e29b-41d4-a716-446655440000",
                    "workflow_name": "Leave Request Approval"
                },
                "document": {
                    "type": "leave_request",
                    "id": "cc0e8400-e29b-41d4-a716-446655440000",
                    "title": "Leave Request - John Doe",
                    "summary": {
                        "start_date": "2025-08-01",
                        "end_date": "2025-08-05",
                        "days": 5
                    }
                },
                "stage_name": "Manager Approval",
                "priority": "high",
                "status": "pending",
                "assigned_at": "2025-07-25T10:01:00Z",
                "due_date": "2025-07-26T10:01:00Z",
                "zones": [2],
                "available_actions": ["approve", "reject", "return"]
            }
        ],
        "pagination": {
            "total": 15,
            "page": 1,
            "page_size": 20
        }
    }
}
```

### 4.5 Get Task Details
**Endpoint:** `GET /tasks/{task_id}`  
**Description:** Get detailed information about a specific task

**Path Parameters:**
- `task_id` (UUID, required): Task identifier

**Response:** Detailed task information including document data based on zone permissions

### 4.6 Perform Task Action
**Endpoint:** `POST /tasks/{task_id}/action`  
**Description:** Perform action on assigned task

**Path Parameters:**
- `task_id` (UUID, required): Task identifier

**Request Body:**
```json
{
    "action": "approve",
    "comments": "Approved as per policy",
    "data": {
        "approved_amount": 9500,
        "conditions": ["submit_receipts"]
    }
}
```

**Available Actions:**
- `approve`: Approve and move to next stage
- `reject`: Reject and end workflow
- `return`: Return to previous stage
- `delegate`: Delegate to another user
- `save`: Save progress without completing

**Response:**
```json
{
    "success": true,
    "data": {
        "task_id": "ff0e8400-e29b-41d4-a716-446655440000",
        "action": "approve",
        "status": "completed",
        "next_stage": {
            "name": "HR Processing",
            "assignees": ["hr_team"]
        },
        "completed_at": "2025-07-25T11:00:00Z"
    }
}
```

### 4.7 Delegate Task
**Endpoint:** `POST /tasks/{task_id}/delegate`  
**Description:** Delegate task to another user

**Path Parameters:**
- `task_id` (UUID, required): Task identifier

**Request Body:**
```json
{
    "delegate_to": "330e8400-e29b-41d4-a716-446655440000",
    "reason": "Out of office",
    "return_after_completion": false
}
```

### 4.8 Get Task History
**Endpoint:** `GET /tasks/{task_id}/history`  
**Description:** Get action history for a task

**Path Parameters:**
- `task_id` (UUID, required): Task identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "history": [
            {
                "id": "440e8400-e29b-41d4-a716-446655440000",
                "action": "assigned",
                "user": {
                    "id": "aa0e8400-e29b-41d4-a716-446655440000",
                    "full_name": "John Manager"
                },
                "timestamp": "2025-07-25T10:01:00Z",
                "details": {
                    "assigned_by": "system"
                }
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "action": "viewed",
                "user": {
                    "id": "aa0e8400-e29b-41d4-a716-446655440000",
                    "full_name": "John Manager"
                },
                "timestamp": "2025-07-25T10:30:00Z"
            }
        ]
    }
}
```

## 5. Analytics API

### 5.1 Workflow Analytics
**Endpoint:** `GET /analytics/workflows/{workflow_id}`  
**Description:** Get analytics for specific workflow

**Path Parameters:**
- `workflow_id` (UUID, required): Workflow identifier

**Query Parameters:**
- `date_from` (date, required): Start date
- `date_to` (date, required): End date
- `group_by` (string): Grouping (day, week, month)

**Response:**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_instances": 150,
            "completed": 120,
            "in_progress": 25,
            "cancelled": 5,
            "average_completion_time": 25200,
            "sla_compliance_rate": 0.92
        },
        "trends": [
            {
                "date": "2025-07-01",
                "started": 10,
                "completed": 8,
                "avg_time": 21600
            }
        ],
        "bottlenecks": [
            {
                "stage": "Manager Approval",
                "average_time": 14400,
                "pending_count": 15
            }
        ]
    }
}
```

### 5.2 User Performance Analytics
**Endpoint:** `GET /analytics/users/{user_id}/performance`  
**Description:** Get user performance metrics

**Path Parameters:**
- `user_id` (UUID, required): User identifier

**Query Parameters:**
- `date_from` (date, required): Start date
- `date_to` (date, required): End date

**Response:**
```json
{
    "success": true,
    "data": {
        "tasks_summary": {
            "total_assigned": 85,
            "completed": 80,
            "pending": 5,
            "average_completion_time": 7200,
            "on_time_rate": 0.94
        },
        "by_workflow": [
            {
                "workflow_name": "Leave Request Approval",
                "count": 45,
                "avg_time": 3600
            }
        ]
    }
}
```

### 5.3 SLA Report
**Endpoint:** `GET /analytics/sla`  
**Description:** Get SLA compliance report

**Query Parameters:**
- `workflow_id` (UUID): Filter by workflow
- `date_from` (date, required): Start date
- `date_to` (date, required): End date

**Response:**
```json
{
    "success": true,
    "data": {
        "overall_compliance": 0.89,
        "by_workflow": [
            {
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "workflow_name": "Leave Request Approval",
                "compliance_rate": 0.95,
                "total_instances": 50,
                "breached": 2,
                "stages": [
                    {
                        "stage_name": "Manager Approval",
                        "sla_hours": 24,
                        "compliance_rate": 0.96,
                        "average_time": 18.5
                    }
                ]
            }
        ]
    }
}
```

## 6. Webhook API

### 6.1 Register Webhook
**Endpoint:** `POST /webhooks`  
**Description:** Register a new webhook

**Request Body:**
```json
{
    "url": "https://example.com/webhook",
    "events": [
        "workflow.started",
        "task.assigned",
        "task.completed",
        "workflow.completed"
    ],
    "active": true,
    "headers": {
        "X-Custom-Header": "value"
    }
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440000",
        "url": "https://example.com/webhook",
        "secret": "whsec_1234567890abcdef",
        "events": ["workflow.started", "task.assigned", "task.completed", "workflow.completed"],
        "active": true,
        "created_at": "2025-07-25T10:00:00Z"
    }
}
```

### 6.2 Webhook Event Payload
**Event Structure:**
```json
{
    "id": "evt_770e8400-e29b-41d4-a716-446655440000",
    "type": "task.assigned",
    "created": 1627462800,
    "data": {
        "task": {
            "id": "ff0e8400-e29b-41d4-a716-446655440000",
            "runtime_id": "dd0e8400-e29b-41d4-a716-446655440000",
            "assignee_id": "aa0e8400-e29b-41d4-a716-446655440000",
            "stage_name": "Manager Approval"
        },
        "workflow": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Leave Request Approval"
        },
        "document": {
            "type": "leave_request",
            "id": "cc0e8400-e29b-41d4-a716-446655440000"
        }
    }
}
```

**Webhook Security:**
- All webhooks include HMAC signature in `X-Webhook-Signature` header
- Verify using webhook secret: `HMAC-SHA256(payload, secret)`

### 6.3 List Webhooks
**Endpoint:** `GET /webhooks`  
**Description:** List all registered webhooks

**Response:**
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "url": "https://example.com/webhook",
                "events": ["workflow.started", "task.assigned"],
                "active": true,
                "created_at": "2025-07-25T10:00:00Z",
                "last_delivery": {
                    "timestamp": "2025-07-25T11:00:00Z",
                    "status": "success"
                }
            }
        ]
    }
}
```

### 6.4 Get Webhook Deliveries
**Endpoint:** `GET /webhooks/{webhook_id}/deliveries`  
**Description:** Get delivery history for a webhook

**Path Parameters:**
- `webhook_id` (UUID, required): Webhook identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "deliveries": [
            {
                "id": "880e8400-e29b-41d4-a716-446655440000",
                "event_type": "task.assigned",
                "status": "success",
                "response_code": 200,
                "delivered_at": "2025-07-25T11:00:00Z",
                "attempts": 1
            }
        ]
    }
}
```

## 7. Integration API

### 7.1 ERP Module Integration
**Endpoint:** `POST /integrations/erp/sync`  
**Description:** Sync workflow data with ERP modules

**Request Body:**
```json
{
    "module": "leave_management",
    "action": "sync_approval",
    "data": {
        "runtime_id": "dd0e8400-e29b-41d4-a716-446655440000",
        "leave_request_id": "cc0e8400-e29b-41d4-a716-446655440000",
        "approval_status": "approved"
    }
}
```

### 7.2 External System Integration
**Endpoint:** `POST /integrations/external`  
**Description:** Trigger external system integration

**Request Body:**
```json
{
    "system": "sap",
    "endpoint": "purchase_order",
    "method": "create",
    "data": {
        "po_number": "PO-2025-001",
        "amount": 10000,
        "workflow_id": "dd0e8400-e29b-41d4-a716-446655440000"
    }
}
```

## 8. Administrative API

### 8.1 User Management
**Endpoint:** `GET /admin/users`  
**Description:** List users with workflow permissions

**Query Parameters:**
- `role` (string): Filter by role
- `department` (UUID): Filter by department
- `has_tasks` (boolean): Users with active tasks

### 8.2 System Health
**Endpoint:** `GET /admin/health`  
**Description:** Get system health status

**Response:**
```json
{
    "success": true,
    "data": {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "database": "healthy",
            "queue": "healthy",
            "cache": "healthy"
        },
        "metrics": {
            "active_workflows": 125,
            "pending_tasks": 45,
            "queue_size": 12,
            "avg_response_time": 150
        },
        "timestamp": "2025-07-25T12:00:00Z"
    }
}
```

## 9. Error Codes Reference

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| AUTH_001 | Invalid credentials | 401 |
| AUTH_002 | Token expired | 401 |
| AUTH_003 | Insufficient permissions | 403 |
| WF_001 | Workflow not found | 404 |
| WF_002 | Workflow already applied | 409 |
| WF_003 | Invalid workflow configuration | 422 |
| RT_001 | Runtime not found | 404 |
| RT_002 | Invalid action for current state | 422 |
| RT_003 | Task already completed | 409 |
| VAL_001 | Validation error | 422 |
| SYS_001 | Internal server error | 500 |
| RATE_001 | Rate limit exceeded | 429 |

## 10. SDK Examples

### 10.1 JavaScript/TypeScript
```typescript
import { BflowClient } from '@bflow/sdk';

const client = new BflowClient({
    baseUrl: 'https://api.bflow.com/api/v1',
    apiKey: 'your-api-key'
});

// Create workflow instance
const runtime = await client.runtime.execute({
    workflowId: '550e8400-e29b-41d4-a716-446655440000',
    documentType: 'leave_request',
    documentId: 'cc0e8400-e29b-41d4-a716-446655440000'
});

// Get user tasks
const tasks = await client.tasks.list({
    status: 'pending',
    priority: 'high'
});

// Perform action
await client.tasks.action(taskId, {
    action: 'approve',
    comments: 'Approved'
});
```

### 10.2 Python
```python
from bflow import BflowClient

client = BflowClient(
    base_url='https://api.bflow.com/api/v1',
    api_key='your-api-key'
)

# Create workflow instance
runtime = client.runtime.execute(
    workflow_id='550e8400-e29b-41d4-a716-446655440000',
    document_type='leave_request',
    document_id='cc0e8400-e29b-41d4-a716-446655440000'
)

# Get user tasks
tasks = client.tasks.list(status='pending', priority='high')

# Perform action
client.tasks.action(
    task_id=task_id,
    action='approve',
    comments='Approved'
)
```

### 10.3 cURL Examples
```bash
# Get workflows
curl -X GET "https://api.bflow.com/api/v1/workflows" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"

# Execute workflow
curl -X POST "https://api.bflow.com/api/v1/runtime/execute" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
    "document_type": "leave_request",
    "document_id": "cc0e8400-e29b-41d4-a716-446655440000"
  }'

# Perform task action
curl -X POST "https://api.bflow.com/api/v1/tasks/<task_id>/action" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "comments": "Approved as per policy"
  }'
```

## 11. API Versioning

### 11.1 Version Strategy
- Current version: v1
- Version in URL path: `/api/v1/`
- Deprecation notice: 6 months
- Sunset period: 12 months

### 11.2 Version Headers
```http
X-API-Version: 1.0
X-API-Deprecation-Date: 2026-01-01
X-API-Sunset-Date: 2026-07-01
```

## 12. Rate Limiting

### 12.1 Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1627466400
```

### 12.2 Rate Limit Response
```json
{
    "success": false,
    "errors": [
        {
            "code": "RATE_001",
            "message": "API rate limit exceeded",
            "retry_after": 3600
        }
    ]
}
```

## 13. Best Practices

### 13.1 Pagination
- Always use pagination for list endpoints
- Default page size: 20
- Maximum page size: 100
- Use cursor-based pagination for large datasets

### 13.2 Filtering
- Use query parameters for filtering
- Support multiple filters with AND logic
- Use comma-separated values for OR logic

### 13.3 Error Handling
- Always check `success` field
- Handle specific error codes
- Implement exponential backoff for retries
- Log error request IDs for support

### 13.4 Performance
- Use field selection to reduce payload
- Implement caching where appropriate
- Use webhooks instead of polling
- Batch operations when possible

---
**Document Control:**
- Version: 1.0
- Last Updated: 2025-07-25
- Review Cycle: Monthly
- API Support: api-support@bflow.com
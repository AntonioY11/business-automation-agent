const API_URL = "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function apiFetch(path: string, init?: RequestInit) {
  try {
    return await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new ApiError(
      "Cannot reach the API. Check that the backend is running.",
      0
    );
  }
}

async function failure(response: Response, fallback: string) {
  let detail = fallback;

  try {
    const body = await response.json();

    if (typeof body.detail === "string") {
      detail = body.detail;
    }
  } catch {
    detail = fallback;
  }

  return new ApiError(detail, response.status);
}

export type Request = {
  id: number;
  customer_id: number;
  raw_text: string;
  status: string;
  intent: string | null;
  priority: string | null;
  account_id: string | null;
  created_at: string;
  error_message: string | null;
  action_result: string | null;
};

export type Customer = {
  id: number;
  name: string;
  email: string;
  subscription_status: string;
  address: string | null;
};


export type Approval = {
  id: number;
  customer_id: number;
  intent: string;
  account_id: string | null;
  new_address: string | null;
  refund_reason: string | null;
  status: string;
  created_at: string;
};

export type AuditLog = {
  id: number;
  customer_id: number | null;
  event_type: string;
  details: string | null;
  created_at: string;
};


export async function getRequests(): Promise<Request[]> {
  const response = await apiFetch("/requests");

  if (!response.ok) {
    throw await failure(response, "Failed to fetch requests");
  }

  return response.json();
}

export async function getRequest(id: number): Promise<Request> {
  const response = await apiFetch(`/requests/${id}`);

  if (!response.ok) {
    throw await failure(response, "Failed to fetch request");
  }

  return response.json();
}


export async function getCustomers(): Promise<Customer[]> {
  const response = await fetch(`${API_URL}/customers`);

  if (!response.ok) {
    throw new Error("Failed to fetch customers");
  }

  return response.json();
}

export async function getCustomer(id: number): Promise<Customer> {
  const response = await fetch(`${API_URL}/customers/${id}`);

  if (!response.ok) {
    throw new Error("Failed to fetch customer");
  }

  return response.json();
}

export async function getCustomerRequests(
  customerId: number
): Promise<Request[]> {
  const response = await fetch(
    `${API_URL}/customers/${customerId}/requests`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch customer requests");
  }

  return response.json();
}


export async function getApprovals(): Promise<Approval[]> {
  const response = await fetch(`${API_URL}/approvals`);

  if (!response.ok) {
    throw new Error("Failed to fetch approvals");
  }

  return response.json();
}


export async function approveApproval(id: number) {
  const response = await fetch(
    `${API_URL}/approvals/${id}/approve`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to approve approval");
  }

  return response.json();
}

export async function rejectApproval(id: number) {
  const response = await fetch(
    `${API_URL}/approvals/${id}/reject`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to reject approval");
  }

  return response.json();
}

export async function getAuditLogs(): Promise<AuditLog[]> {
  const response = await fetch(`${API_URL}/audit-logs`);

  if (!response.ok) {
    throw new Error("Failed to fetch audit logs");
  }

  return response.json();
}

export type CreateRequestResult = {
  request: Request;
  action: {
    success: boolean;
    message: string;
    status?: string;
  };
  customer_message: string;
};

export async function createRequest(
  customerId: number,
  rawText: string
): Promise<CreateRequestResult> {
  const response = await apiFetch("/requests", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      customer_id: customerId,
      raw_text: rawText,
    }),
  });

  if (!response.ok) {
    throw await failure(response, "Failed to create request");
  }

  return response.json();
}
import type { Page } from "@playwright/test"
import config from "../config"

/**
 * API helper for direct backend calls (bypassing frontend)
 */
export class PrivateApi {
  constructor(private page: Page) {}

  /**
   * Check backend health
   */
  async checkHealth() {
    const response = await this.page.request.get(`${config.apiURL}/health`)
    return response.json()
  }

  /**
   * Make authenticated API call
   */
  async authenticatedRequest(
    method: "GET" | "POST" | "PUT" | "DELETE",
    endpoint: string,
    token: string,
    data?: any
  ) {
    const options: any = {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    }

    if (data) {
      options.data = data
    }

    const response = await this.page.request[method.toLowerCase() as "get" | "post" | "put" | "delete"](
      `${config.apiURL}${endpoint}`,
      options
    )

    return {
      status: response.status(),
      data: await response.json().catch(() => ({})),
    }
  }
}

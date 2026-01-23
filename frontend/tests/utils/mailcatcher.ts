import { expect, type Page } from "@playwright/test"
import config from "./config"

/**
 * Mailcatcher API helper
 */
export class Mailcatcher {
  constructor(private page: Page) {}

  /**
   * Get all emails from Mailcatcher
   */
  async getMessages() {
    const response = await this.page.request.get(`${config.mailcatcherURL}/messages`)
    expect(response.ok()).toBeTruthy()
    return response.json()
  }

  /**
   * Get a specific email by ID
   */
  async getMessage(id: string) {
    const response = await this.page.request.get(`${config.mailcatcherURL}/messages/${id}.json`)
    expect(response.ok()).toBeTruthy()
    return response.json()
  }

  /**
   * Delete all emails
   */
  async clearMessages() {
    await this.page.request.delete(`${config.mailcatcherURL}/messages`)
  }

  /**
   * Wait for an email matching a condition
   */
  async waitForEmail(
    condition: (message: any) => boolean,
    timeout = 10000
  ): Promise<any> {
    const startTime = Date.now()

    while (Date.now() - startTime < timeout) {
      const messages = await this.getMessages()
      const match = messages.find(condition)

      if (match) {
        return match
      }

      await this.page.waitForTimeout(500)
    }

    throw new Error("Email not found within timeout")
  }

  /**
   * Get email by subject
   */
  async getEmailBySubject(subject: string) {
    return this.waitForEmail((msg) => msg.subject === subject)
  }

  /**
   * Get email by recipient
   */
  async getEmailByRecipient(recipient: string) {
    return this.waitForEmail((msg) =>
      msg.recipients.includes(`<${recipient}>`)
    )
  }
}

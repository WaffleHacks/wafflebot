/**
 * Add the success field if necessary
 * @param content {Object} the JSON response
 * @param response {Response} the resulting response
 * @returns {{data: Object, success: boolean, status: number}}
 */
function addSuccess(content, response) {
  if (response.status === 200) return { success: true, data: content, status: response.status };
  return { status: response.status, ...content };
}

export class User {
  /**
   * Get the user's information
   * @returns {Promise<{data: Object, success: boolean}>}
   */
  static async info(signal = undefined) {
    const response = await fetch("/api/authentication/me", { signal });
    const content = await response.json();
    return addSuccess(content, response);
  }

  /**
   * Logout the user
   */
  static async logout(signal = undefined) {
    await fetch("/api/authentication/logout", { signal });
  }
}

export class CannedResponse {
  /**
   * Get a list of all the canned responses
   * @returns {Promise<{data: Object, success: boolean}>}
   */
  static async list() {
    const response = await fetch("/api/canned-responses/");
    const content = await response.json();
    return addSuccess(content, response);
  }

  /**
   * Create a canned response
   * @param key {string} the key that the response is referenced by
   * @param title {string} the response's title
   * @param content {string} the response's content
   * @param fields {Object} optional fields
   * @returns {Promise<{data: Object, success: boolean}>}
   */
  static async create(key, title, content, fields = {}) {
    const response = await fetch("/api/canned-responses/", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, title, content, fields }),
    });
    const data = await response.json();
    return addSuccess(data, response);
  }

  /**
   * Modify a canned response
   * @param id {number} the primary key
   * @param key {string} the key that the response is referenced by
   * @param title {string} the response's title
   * @param content {string} the response's content
   * @param fields {Object} optional fields
   * @returns {Promise<{data: Object, success: boolean}>}
   */
  static async update(id, key, title, content, fields = {}) {
    const response = await fetch(`/api/canned-responses/${id}`, {
      method: "PUT",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, title, content, fields }),
    });
    const data = await response.json();
    return addSuccess(data, response);
  }

  /**
   * Delete a canned response
   * @param id {number} the primary key
   * @returns {Promise<boolean>}
   */
  static async delete(id) {
    const response = await fetch(`/api/canned-responses/${id}`, { method: "DELETE" });
    return response.status === 200;
  }
}

export class Settings {
  /**
   * List all the settings
   * @returns {Promise<{data: Object, success: boolean, status: number}>}
   */
  static async list() {
    const response = await fetch("/api/settings/");
    const data = await response.json();
    return addSuccess(data, response);
  }

  /**
   * Modify a setting parameter
   * @param key {string} the setting key
   * @param value {number} the new value
   * @returns {Promise<{data: Object, success: boolean, status: number}>}
   */
  static async update(key, value) {
    const response = await fetch(`/api/settings/${key}`, {
      method: "PUT",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value }),
    });
    const data = await response.json();
    return addSuccess(data, response);
  }

  /**
   * Get a list of the roles in the Discord
   * @returns {Promise<{data: Array<{name: string, id: string, color: string}>, success: boolean, status: number}>}
   */
  static async roles() {
    const response = await fetch("/api/settings/roles", {
      credentials: "same-origin",
    });
    const data = await response.json();
    return addSuccess(data, response);
  }
}

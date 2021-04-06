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
    const response = await fetch("/authentication/me", { signal });
    const content = await response.json();
    return addSuccess(content, response);
  }

  /**
   * Logout the user
   */
  static async logout(signal = undefined) {
    await fetch("/authentication/logout", { signal });
  }
}

export class CannedResponse {
  /**
   * Get a list of all the canned responses
   * @returns {Promise<{data: Object, success: boolean}>}
   */
  static async list() {
    const response = await fetch("/canned-responses/");
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
    const response = await fetch("/canned-responses/", {
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
    const response = await fetch(`/canned-responses/${id}`, {
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
    const response = await fetch(`/canned-responses/${id}`, { method: "DELETE" });
    return response.status === 200;
  }
}

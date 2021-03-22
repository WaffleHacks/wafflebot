export class User {
  /**
   * Get the user's information
   * @returns {Promise<{data: Object, success: boolean}>}
   */
  static async info(signal = undefined) {
    const response = await fetch("/authentication/me", { signal });
    const content = await response.json();

    if (response.status === 200) return { success: true, data: content };
    return content;
  }

  /**
   * Logout the user
   */
  static async logout(signal = undefined) {
    await fetch("/authentication/logout", { signal });
  }
}

import { writable } from "svelte/store";

// Whether the user is authenticated
export const isAuthenticated = writable(false);

// The user's profile information
// TODO: figure out some sort of persistence between page loads
export const user = writable({});

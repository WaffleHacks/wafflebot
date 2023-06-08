import { APPLICATION_PORTAL_TOKEN, APPLICATION_PORTAL_URL } from '@lib/config';

export enum Status {
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  PENDING = 'pending',
}

interface StatusResponse {
  id: number;
  status: Status;
}

export interface ApplicationStatus {
  id?: number;
  status: Status | null;
}

/**
 * Lookup the status of an application by the participant's email
 * @param email
 */
export async function lookupApplicationStatusByEmail(email: string): Promise<ApplicationStatus> {
  const data: StatusResponse | null = await request(`status?email=${encodeURIComponent(email)}`);
  if (data === null) return { status: null };
  else return data;
}

export interface UserInfo {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  link: string;
}

/**
 * Lookup a participant's information by their email
 * @param email
 */
export const lookupParticipantByEmail = async (email: string): Promise<UserInfo | null> =>
  request(`lookup?email=${encodeURIComponent(email)}`);

/**
 * Lookup a participant's information by their application portal ID
 * @param id
 */
export const lookupParticipantByID = async (id: number): Promise<UserInfo | null> => request(`lookup?id=${id}`);

async function request<T>(pathAndQuery: string): Promise<T> {
  const response = await fetch(`${APPLICATION_PORTAL_URL}/integrations/wafflebot/${pathAndQuery}`, {
    headers: {
      Authorization: `Bearer ${APPLICATION_PORTAL_TOKEN}`,
    },
  });
  if (response.status !== 200) throw new Error(`unexpected response: ${await response.text()} (${response.status})`);

  return await response.json();
}

import { APPLICATION_PORTAL_TOKEN, APPLICATION_PORTAL_URL } from '@lib/config';

export enum Status {
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  PENDING = 'pending',
}

interface StatusResponse {
  status: Status | null;
}

/**
 * Lookup the status of an application by the participant's email
 * @param email
 */
export async function lookupApplicationStatusByEmail(email: string): Promise<Status | null> {
  const response = await fetch(
    `${APPLICATION_PORTAL_URL}/integrations/wafflebot/status?email=${encodeURIComponent(email)}`,
    {
      headers: {
        Authorization: `Bearer ${APPLICATION_PORTAL_TOKEN}`,
      },
    },
  );
  const data: StatusResponse = await response.json();

  return data.status;
}

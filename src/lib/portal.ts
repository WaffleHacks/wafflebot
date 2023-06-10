import { context, propagation } from '@opentelemetry/api';

import { APPLICATION_PORTAL_TOKEN, APPLICATION_PORTAL_URL } from '@lib/config';
import { inSpan } from '@lib/tracing';

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
  inSpan('lookup', (span) => {
    span.setAttributes({ 'lookup.by': 'email', 'lookup.email': email });
    return request(`lookup?email=${encodeURIComponent(email)}`);
  });

/**
 * Lookup a participant's information by their application portal ID
 * @param id
 */
export const lookupParticipantByID = async (id: number): Promise<UserInfo | null> =>
  inSpan('lookup', (span) => {
    span.setAttributes({ 'lookup.by': 'id', 'lookup.id': id });
    return request(`lookup?id=${id}`);
  });

const request = <T>(pathAndQuery: string): Promise<T> =>
  inSpan('request', async (span) => {
    const url = `${APPLICATION_PORTAL_URL}/integrations/wafflebot/${pathAndQuery}`;

    span.setAttributes({ 'http.request.method': 'GET', 'http.request.url': url });

    const headers: HeadersInit = { Authorization: `Bearer ${APPLICATION_PORTAL_TOKEN}` };
    propagation.inject(context.active(), headers);

    const response = await fetch(url, { headers });

    if (response.status !== 200) throw new Error(`unexpected response: ${await response.text()} (${response.status})`);
    else return await response.json();
  });

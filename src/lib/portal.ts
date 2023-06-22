import { context, propagation } from '@opentelemetry/api';

import { APPLICATION_PORTAL_TOKEN, APPLICATION_PORTAL_URL } from '@lib/config';
import { withSpan } from '@lib/tracing';

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
export const lookupApplicationStatusByEmail = async (email: string): Promise<ApplicationStatus> =>
  withSpan('lookup.application', async (span) => {
    span.setAttribute('lookup.email', email);
    const data: StatusResponse | null = await request(`status?email=${encodeURIComponent(email)}`);
    if (data === null) return { status: null };
    else return data;
  });

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
  await withSpan('lookup.participant', async (span): Promise<UserInfo | null> => {
    span.setAttributes({ 'lookup.by': 'email', 'lookup.email': email });
    return await request(`lookup?email=${encodeURIComponent(email)}`);
  });

/**
 * Lookup a participant's information by their application portal ID
 * @param id
 */
export const lookupParticipantByID = async (id: number): Promise<UserInfo | null> =>
  await withSpan('lookup.participant', async (span): Promise<UserInfo | null> => {
    span.setAttributes({ 'lookup.by': 'id', 'lookup.id': id });
    return await request(`lookup?id=${id}`);
  });

export interface EventDetails {
  id: number;
  name: string;
  url: string;
  description: string | null;
  start: string;
  end: string;
}

export const findEvent = async (id: number): Promise<EventDetails | null> =>
  await withSpan('events.find', async (span): Promise<EventDetails | null> => {
    span.setAttribute('event.id', id);
    return await request(`events/${id}`);
  });

export const listEvents = async (): Promise<EventDetails[]> =>
  await withSpan('events.list', async (): Promise<EventDetails[]> => request('events'));

const request = async <T>(pathAndQuery: string): Promise<T> =>
  await withSpan('request', async (span) => {
    const url = `${APPLICATION_PORTAL_URL}/integrations/wafflebot/${pathAndQuery}`;

    span.setAttributes({ 'http.request.method': 'GET', 'http.request.url': url });

    const headers: HeadersInit = { Authorization: `Bearer ${APPLICATION_PORTAL_TOKEN}` };
    propagation.inject(context.active(), headers);

    const response = await fetch(url, { headers });
    span.setAttribute('http.response.status', response.status);

    if (response.status !== 200) throw new Error(`unexpected response: ${await response.text()} (${response.status})`);
    else return await response.json();
  });

export const checkInParticipant = async (ids: number | number[]): Promise<boolean> =>
  await withSpan('request', async (span) => {
    const url = `${APPLICATION_PORTAL_URL}/integrations/wafflebot/check-in`;
    span.setAttributes({ 'http.request.method': 'PUT', 'http.request.url': url });

    const headers: HeadersInit = {
      Authorization: `Bearer ${APPLICATION_PORTAL_TOKEN}`,
      'Content-Type': 'application/json',
    };
    propagation.inject(context.active(), headers);

    const response = await fetch(url, { method: 'PUT', headers, body: JSON.stringify({ participant: ids }) });
    span.setAttribute('http.response.status', response.status);

    if (response.status === 204) return true;
    else if (response.status === 400) return false;
    else throw new Error(`unexpected response: ${await response.text()} (${response.status})`);
  });

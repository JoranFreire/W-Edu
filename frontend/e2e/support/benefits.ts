import type { APIRequestContext } from '@playwright/test';
import { API_URL, adminHeaders } from './api';

/** Item de beneficio com estoque (preparo: o foco do teste e liberar e validar o QR). */
export async function createBenefitItemWithStock(
  request: APIRequestContext, name: string, quantity: number, kind: 'snack' | 'material' = 'snack', institution = 'escola-alfa',
) {
  const admin = await adminHeaders(request, institution);
  const item = await request.post(`${API_URL}/social/benefit-items`, {
    headers: admin, data: { name, kind, unit: kind === 'snack' ? 'unidade' : 'kit', unit_cost_cents: 500, requires_attendance: kind === 'snack' },
  });
  if (!item.ok()) throw new Error(`benefit item: ${item.status()} ${await item.text()}`);
  const { id }: { id: string } = await item.json();
  const stock = await request.post(`${API_URL}/social/benefit-items/${id}/stock`, {
    headers: admin, data: { quantity, received_on: new Date().toISOString().slice(0, 10) },
  });
  if (!stock.ok()) throw new Error(`benefit stock: ${stock.status()} ${await stock.text()}`);
  return { id, name };
}

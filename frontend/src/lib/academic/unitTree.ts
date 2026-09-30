import type { AcademicUnit } from '@/types/academic';

export interface UnitRow {
  unit: AcademicUnit;
  depth: number;
}

/** Ordena as unidades em pre-ordem (pai antes dos filhos), com a profundidade de cada uma. */
export function flattenUnits(units: AcademicUnit[]): UnitRow[] {
  const ids = new Set(units.map((unit) => unit.id));
  const childrenOf = (parentId: number | null) =>
    units
      .filter((unit) => (parentId === null ? unit.parent_id === null || !ids.has(unit.parent_id) : unit.parent_id === parentId))
      .sort((a, b) => a.name.localeCompare(b.name));
  const rows: UnitRow[] = [];
  const visit = (parentId: number | null, depth: number) => {
    for (const unit of childrenOf(parentId)) {
      rows.push({ unit, depth });
      visit(unit.id, depth + 1);
    }
  };
  visit(null, 0);
  return rows;
}

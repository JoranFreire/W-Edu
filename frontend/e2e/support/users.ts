/** Usuarios criados por backend/scripts/seed_e2e.py (mesma senha). */
export const E2E_PASSWORD = 'e2e-senha-123';

export const users = {
  admin: 'admin@alfa.example.com', // institution_admin da Escola Alfa e da Faculdade Beta
  aluno: 'aluno@alfa.example.com',
  instrutor: 'instrutor@alfa.example.com',
  root: 'root@e2e.example.com', // super_admin
} as const;

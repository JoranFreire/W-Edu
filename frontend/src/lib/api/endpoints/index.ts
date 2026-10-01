/** Rotas da API por area de negocio; `endpoints` reune todas (um modulo por area em ./). */
import { identityEndpoints } from './identity';
import { academicEndpoints } from './academic';
import { assessmentEndpoints } from './assessment';
import { secretariatEndpoints } from './secretariat';
import { familyEndpoints } from './family';
import { financeEndpoints } from './finance';
import { admissionsEndpoints } from './admissions';
import { socialEndpoints } from './social';
import { warehouseEndpoints } from './warehouse';
import { learningEndpoints } from './learning';
import { scheduleEndpoints } from './schedule';
import { communicationEndpoints } from './communication';
import { reportsEndpoints } from './reports';

export const endpoints = {
  ...identityEndpoints,
  ...academicEndpoints,
  ...assessmentEndpoints,
  ...secretariatEndpoints,
  ...familyEndpoints,
  ...financeEndpoints,
  ...admissionsEndpoints,
  ...socialEndpoints,
  ...warehouseEndpoints,
  ...learningEndpoints,
  ...scheduleEndpoints,
  ...communicationEndpoints,
  ...reportsEndpoints,
};

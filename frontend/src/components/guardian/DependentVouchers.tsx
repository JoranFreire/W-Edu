'use client';

import Spinner from '@/components/common/Spinner';
import VoucherList from '@/components/social/vouchers/VoucherList';
import { useDependentVouchers } from '@/lib/hooks/guardian/useDependentVouchers';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function DependentVouchers({ studentId }: { studentId: string }) {
  const { vouchers, loading, error } = useDependentVouchers(studentId);
  useErrorToast(error, 'Erro ao carregar os benefícios.');
  return loading && vouchers.length === 0 ? <Spinner /> : <VoucherList vouchers={vouchers} />;
}

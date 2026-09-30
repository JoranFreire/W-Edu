import { MapPinIcon } from '@heroicons/react/24/outline';
import StatusBadge from '@/components/common/StatusBadge';
import type { Location, Room } from '@/types/schedule';

export default function LocationsList({ locations, rooms }: { locations: Location[]; rooms: Room[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      {locations.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhuma unidade cadastrada.</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {locations.map((location) => {
            const roomCount = rooms.filter((room) => room.location_id === location.id).length;
            return (
              <div key={location.id} className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-900/20">
                    <MapPinIcon className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{location.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {location.address || 'Endereço não informado'} · {roomCount} {roomCount === 1 ? 'sala' : 'salas'}
                    </p>
                  </div>
                </div>
                <StatusBadge active={location.is_active} />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

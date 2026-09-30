import { BuildingOffice2Icon } from '@heroicons/react/24/outline';
import StatusBadge from '@/components/common/StatusBadge';
import type { Location, Room } from '@/types/schedule';

export default function RoomsList({ rooms, locations }: { rooms: Room[]; locations: Location[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      {rooms.length === 0 ? (
        <p className="p-5 text-sm text-gray-500 dark:text-gray-400">Nenhuma sala cadastrada.</p>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-700">
          {rooms.map((room) => {
            const location = locations.find((item) => item.id === room.location_id);
            return (
              <div key={room.id} className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 dark:bg-indigo-900/20">
                    <BuildingOffice2Icon className="h-5 w-5 text-indigo-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{room.name}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {location?.name ?? `Unidade #${room.location_id}`} · {room.capacity} lugares
                    </p>
                  </div>
                </div>
                <StatusBadge active={room.is_active} />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

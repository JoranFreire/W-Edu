export default function BrandingPreview({ name, logoUrl }: { name: string; logoUrl: string }) {
  return (
    <div className="mt-5 flex items-center gap-3 rounded-lg bg-gray-900 px-4 py-3">
      {logoUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={logoUrl} alt="" className="h-8 w-8 rounded-lg bg-white object-contain" />
      ) : (
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
          <span className="text-lg font-bold text-white">{name.charAt(0).toUpperCase()}</span>
        </div>
      )}
      <span className="text-lg font-bold text-white">{name}</span>
      <span className="ml-auto rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white">Botão</span>
    </div>
  );
}

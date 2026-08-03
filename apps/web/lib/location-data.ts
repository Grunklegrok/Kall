import { allCountries } from 'country-region-data';

export type LocationOption = {
  code: string;
  name: string;
};

export const countries: LocationOption[] = allCountries
  .map(([name, code]) => ({ code, name }))
  .sort((a, b) => a.name.localeCompare(b.name));

export function regionsForCountry(countryCode: string): LocationOption[] {
  const country = allCountries.find(([, code]) => code === countryCode);
  if (!country) return [];

  return country[2]
    .map(([name, code]) => ({ code, name }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function countryName(countryCode: string): string | null {
  return allCountries.find(([, code]) => code === countryCode)?.[0] ?? null;
}

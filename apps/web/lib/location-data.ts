import { allCountries } from 'country-region-data';

export type LocationOption = {
  code: string;
  name: string;
};

export const countries: LocationOption[] = allCountries
  .map((country) => ({
    code: country.countryShortCode,
    name: country.countryName,
  }))
  .sort((a, b) => a.name.localeCompare(b.name));

export function regionsForCountry(countryCode: string): LocationOption[] {
  const country = allCountries.find((item) => item.countryShortCode === countryCode);
  if (!country) return [];

  return country.regions
    .map((region) => ({
      code: region.shortCode,
      name: region.name,
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function countryName(countryCode: string): string | null {
  return allCountries.find((item) => item.countryShortCode === countryCode)?.countryName ?? null;
}

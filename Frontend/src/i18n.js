// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Importing translation resources from public/locales folder
import translationEN from './locales/en.json';
import translationHI from './locales/hi.json';

i18n
    .use(initReactI18next) // Passes i18n down to react-i18next
    .init({
        resources: {
            en: {
                translation: translationEN
            },
            hi: {
                translation: translationHI
            }
        },
        lng: 'en', // Default language
        fallbackLng: 'en', // Fallback language if translation is not available in selected language
        interpolation: {
            escapeValue: false // React already does escaping by default
        }
    });

export default i18n;

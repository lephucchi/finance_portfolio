import { useState, useEffect } from 'react';
import { t, setLanguage, getLanguage, Language } from '@/lib/i18n';

// Global listeners for language changes
const languageListeners: ((lang: Language) => void)[] = [];

export const subscribeToLanguageChange = (callback: (lang: Language) => void) => {
  languageListeners.push(callback);
  return () => {
    const index = languageListeners.indexOf(callback);
    if (index > -1) {
      languageListeners.splice(index, 1);
    }
  };
};

export const notifyLanguageChange = (lang: Language) => {
  languageListeners.forEach(callback => callback(lang));
};

export const useI18n = () => {
  const [language, setLang] = useState<Language>(() => getLanguage());
  
  useEffect(() => {
    const unsubscribe = subscribeToLanguageChange((lang) => {
      setLang(lang);
    });
    return unsubscribe;
  }, []);
  
  const changeLanguage = (lang: Language) => {
    setLanguage(lang);
    setLang(lang);
    notifyLanguageChange(lang);
  };
  
  return {
    t,
    language,
    changeLanguage,
  };
};

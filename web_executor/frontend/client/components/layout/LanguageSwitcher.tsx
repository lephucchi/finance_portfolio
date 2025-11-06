import { useState } from 'react';
import { useI18n } from '@/hooks/useI18n';
import { Language } from '@/lib/i18n';
import { cn } from '@/lib/utils';

interface LanguageSwitcherProps {
  className?: string;
}

export default function LanguageSwitcher({ className }: LanguageSwitcherProps) {
  const { language, changeLanguage } = useI18n();
  const [isOpen, setIsOpen] = useState(false);

  const languages: { code: Language; flag: string; name: string }[] = [
    { code: 'en', flag: '🇺🇸', name: 'English' },
    { code: 'vi', flag: '🇻🇳', name: 'Tiếng Việt' },
  ];

  const currentLang = languages.find((l) => l.code === language) || languages[0];

  const handleLanguageChange = (lang: Language) => {
    changeLanguage(lang);
    setIsOpen(false);
  };

  return (
    <div className={cn('relative inline-block', className)}>
      {/* Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-10 h-10 rounded-full transition-all duration-300',
          'hover:bg-secondary/50 hover:shadow-md',
          'border border-border/30 flex items-center justify-center',
          'text-xl font-semibold',
        )}
        title={`Current language: ${currentLang.name}`}
      >
        {currentLang.flag}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className={cn(
            'absolute top-full right-0 mt-2 rounded-lg shadow-lg',
            'bg-background border border-border/30 overflow-hidden',
            'z-50 animate-in fade-in slide-in-from-top-2 duration-200',
          )}
        >
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => handleLanguageChange(lang.code)}
              className={cn(
                'w-full px-4 py-2 text-left transition-colors duration-200',
                'flex items-center gap-2',
                language === lang.code
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'hover:bg-secondary/50 text-foreground',
              )}
            >
              <span className="text-lg">{lang.flag}</span>
              <span>{lang.name}</span>
              {language === lang.code && (
                <span className="ml-auto text-primary">✓</span>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Close on outside click */}
      {isOpen && (
        <div
          className="fixed inset-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}

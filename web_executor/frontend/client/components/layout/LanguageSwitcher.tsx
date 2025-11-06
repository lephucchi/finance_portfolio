import { useI18n } from '@/hooks/useI18n';
import { Language } from '@/lib/i18n';
import { cn } from '@/lib/utils';

interface LanguageSwitcherProps {
  className?: string;
}

export default function LanguageSwitcher({ className }: LanguageSwitcherProps) {
  const { language, changeLanguage } = useI18n();

  const languages: { code: Language; flag: string; name: string }[] = [
    { code: 'en', flag: '🇺🇸', name: 'English' },
    { code: 'vi', flag: '🇻🇳', name: 'Tiếng Việt' },
  ];

  const currentLang = languages.find((l) => l.code === language) || languages[0];
  const nextLang = language === 'en' ? 'vi' : 'en';

  const handleLanguageToggle = () => {
    changeLanguage(nextLang);
  };

  return (
    <button
      onClick={handleLanguageToggle}
      className={cn(
        'w-10 h-10 rounded-full transition-all duration-300',
        'hover:bg-secondary/50 hover:shadow-md',
        'border border-border/30 flex items-center justify-center',
        'text-xl font-semibold',
      )}
      title={`Switch from ${currentLang.name} to ${languages.find((l) => l.code === nextLang)?.name}`}
    >
      {currentLang.flag}
    </button>
  );
}

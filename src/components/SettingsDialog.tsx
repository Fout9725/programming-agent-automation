import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

interface SettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SettingsDialog = ({ open, onOpenChange }: SettingsDialogProps) => {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const savedKey = localStorage.getItem('openrouter_api_key');
    if (savedKey) setApiKey(savedKey);
  }, [open]);

  const handleSave = () => {
    if (!apiKey.trim()) {
      toast({
        title: 'Ошибка',
        description: 'API ключ не может быть пустым',
        variant: 'destructive'
      });
      return;
    }

    localStorage.setItem('openrouter_api_key', apiKey);
    toast({
      title: 'Сохранено!',
      description: 'API ключ успешно сохранен'
    });
    onOpenChange(false);
  };

  const handleClear = () => {
    localStorage.removeItem('openrouter_api_key');
    setApiKey('');
    toast({
      title: 'Очищено',
      description: 'API ключ удален'
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Icon name="Settings" size={20} />
            Настройки
          </DialogTitle>
          <DialogDescription>
            Настройте API ключ для работы с AI моделями
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="api-key">OpenRouter API Key</Label>
            <div className="flex gap-2">
              <Input
                id="api-key"
                type={showKey ? 'text' : 'password'}
                placeholder="sk-or-v1-..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => setShowKey(!showKey)}
              >
                <Icon name={showKey ? 'EyeOff' : 'Eye'} size={18} />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Получите ключ на{' '}
              <a
                href="https://openrouter.ai/keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                openrouter.ai/keys
              </a>
            </p>
          </div>

          <div className="bg-muted p-3 rounded-lg space-y-2 text-xs">
            <p className="font-medium">Как получить ключ:</p>
            <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
              <li>Зарегистрируйтесь на openrouter.ai</li>
              <li>Перейдите в раздел Keys</li>
              <li>Создайте новый ключ</li>
              <li>Скопируйте и вставьте сюда</li>
            </ol>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSave} className="flex-1">
              <Icon name="Save" className="mr-2" size={16} />
              Сохранить
            </Button>
            <Button onClick={handleClear} variant="outline">
              <Icon name="Trash2" className="mr-2" size={16} />
              Очистить
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default SettingsDialog;

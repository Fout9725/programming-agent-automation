import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface ProjectResultProps {
  appUrl: string;
  githubUrl: string;
  filesCount: number;
  buildTime: number;
  costUsd: number;
  projectName: string;
}

const ProjectResult = ({ appUrl, githubUrl, filesCount, buildTime, costUsd, projectName }: ProjectResultProps) => {
  return (
    <Card className="border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-400">
          <Icon name="CheckCircle2" size={24} />
          Проект готов!
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Приложение <strong>{projectName}</strong> успешно собрано и развёрнуто.
        </p>

        <div className="flex flex-wrap gap-2">
          {appUrl && (
            <Button asChild>
              <a href={appUrl} target="_blank" rel="noopener noreferrer">
                <Icon name="ExternalLink" size={16} className="mr-1" />
                Открыть приложение
              </a>
            </Button>
          )}
          {githubUrl && (
            <Button variant="outline" asChild>
              <a href={githubUrl} target="_blank" rel="noopener noreferrer">
                <Icon name="Github" size={16} className="mr-1" />
                GitHub
              </a>
            </Button>
          )}
        </div>

        <div className="flex flex-wrap gap-3 pt-2">
          <Badge variant="secondary" className="gap-1">
            <Icon name="FileCode" size={12} />
            {filesCount} файлов
          </Badge>
          <Badge variant="secondary" className="gap-1">
            <Icon name="Clock" size={12} />
            {buildTime}с
          </Badge>
          {costUsd > 0 && (
            <Badge variant="secondary" className="gap-1">
              <Icon name="DollarSign" size={12} />
              ${costUsd.toFixed(2)}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProjectResult;

import type { AnalysisResult } from "@/services/analysis-service";

import { Card, CardHeader, CardBody } from "@heroui/card";
import { Image } from "@heroui/image";
import { Breadcrumbs, BreadcrumbItem } from "@heroui/breadcrumbs";
import { Chip } from "@heroui/chip";
import { ScrollShadow } from "@heroui/scroll-shadow";
import {
  Brain,
  GitCommit,
  Activity,
  XCircle,
  BookOpen,
  Clock,
  FileText,
  Target,
} from "lucide-react";

interface RepoAnalysisProps {
  blurred?: boolean;
  data?: AnalysisResult | null;
}

export function RepoAnalysis({ blurred = false, data }: RepoAnalysisProps) {
  // Extract repo owner and name from URL if available in analysis data
  const getRepoInfo = (commit_analysis) => {
    return { owner: commit_analysis.owner, name: commit_analysis.repo };
  };

  const commit_analysis = data.commit_analysis.analysis;
  const som_analysis = data.som_analysis.analysis;
  const repo_analysis = data.repo_analysis.analysis;

  const { owner, name } = getRepoInfo(commit_analysis);

  return (
    <div className="rounded-large flex items-center justify-center">
      <div className="absolute z-50">
        <p className="font-bold text-2xl" />
      </div>
      <Card
        className={`w-full select-none ${blurred ? "blur-lg" : ""} ${!data?.repo_analysis?.enabled ? "blur-lg" : ""}`}
        radius="lg"
      >
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <Breadcrumbs separator="/">
              <BreadcrumbItem
                startContent={
                  <Image
                    alt="User Avatar"
                    className="rounded-full"
                    height={20}
                    src="https://avatars.githubusercontent.com/u/120694977?v=4"
                    width={20}
                  />
                }
              >
                {owner}
              </BreadcrumbItem>
              <BreadcrumbItem>{name}</BreadcrumbItem>
            </Breadcrumbs>
          </div>
        </CardHeader>

        <CardBody className="pt-2">
          <div className="grid grid-cols-6 grid-rows-1 gap-4">
            <div className="col-span-4 row-span-1 flex flex-col gap-4">
              <Card className="col-span-2 row-span-1 pb-2" radius="lg">
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <GitCommit className="h-5 w-5 text-warning" />
                    <h3 className="text-lg font-bold">Repo Analysis</h3>
                  </div>
                </CardHeader>

                <CardBody>
                  <div className="grid grid-cols-3 gap-4 w-full">
                    <div className="text-center">
                      <Brain className="h-6 w-6 text-warning mx-auto mb-2" />
                      <div className="text-2xl font-bold text-warning">
                        {Math.round(commit_analysis.analysis.ai)}%
                      </div>
                      <div className="text-sm text-default-600">Use of AI</div>
                    </div>
                    <div className="text-center">
                      <Activity className="h-6 w-6 text-primary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-primary">
                        {commit_analysis.total_commits}
                      </div>
                      <div className="text-sm text-default-600">Commits</div>
                    </div>
                    <div className="text-center">
                      <XCircle className="h-6 w-6 text-danger mx-auto mb-2" />
                      <div className="text-2xl font-bold text-danger">
                        {Math.round(commit_analysis.analysis.adequacy)}%
                      </div>
                      <div className="text-sm text-default-600">Adequacy</div>
                    </div>
                  </div>
                </CardBody>
              </Card>

              <Card
                className={`col-span-2 row-span-1 pb-2 ${!data?.som_analysis?.enabled ? "blur-lg" : ""}`}
                radius="lg"
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-secondary" />
                    <h3 className="text-lg font-bold">SoM Analysis</h3>
                  </div>
                </CardHeader>

                <CardBody>
                  <div className="grid grid-cols-3 gap-4 w-full">
                    <div className="text-center">
                      <FileText className="h-6 w-6 text-success mx-auto mb-2" />
                      <div className="text-2xl font-bold text-success">
                        {som_analysis.devlogs_count}
                      </div>
                      <div className="text-sm text-default-600">Devlogs</div>
                    </div>
                    <div className="text-center">
                      <Clock className="h-6 w-6 text-primary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-primary">
                        {som_analysis.ai_analysis.fraud}%
                      </div>
                      <div className="text-sm text-default-600">
                        Time inflation
                      </div>
                    </div>
                    <div className="text-center">
                      <Brain className="h-6 w-6 text-warning mx-auto mb-2" />
                      <div className="text-2xl font-bold text-warning">
                        {Math.round(som_analysis.ai_analysis.adequacy)}%
                      </div>
                      <div className="text-sm text-default-600">
                        Authenticity
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
            <div className="col-span-2 row-span-1 flex flex-col gap-4">
              <Card className="pb-2 h-full" radius="lg">
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-danger" />
                    <h3 className="text-lg font-bold">SlopScore</h3>
                  </div>
                </CardHeader>

                <CardBody className="flex flex-col gap-4">
                  <div className="text-center">
                    <div className="text-5xl font-bold text-danger">
                      {repo_analysis.slopscore}
                      <span className="text-xs text-default-600">/100</span>
                    </div>
                  </div>

                  <div className="flex-1">
                    <ScrollShadow className="h-48 p-3 bg-default-50 rounded-lg">
                      <div className="space-y-2 text-xs">
                        <div className="flex flex-wrap gap-1 mb-3">
                          {repo_analysis.main_factors
                            .slice(0, 6)
                            .map((factor, index) => (
                              <Chip
                                key={index}
                                className="text-xs px-2 py-0.5 h-5"
                                color="warning"
                                size="sm"
                                variant="flat"
                              >
                                {factor.length > 15
                                  ? `${factor.substring(0, 15)}...`
                                  : factor}
                              </Chip>
                            ))}
                        </div>
                        <p>{repo_analysis.reasoning}</p>
                      </div>
                    </ScrollShadow>
                  </div>
                </CardBody>
              </Card>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

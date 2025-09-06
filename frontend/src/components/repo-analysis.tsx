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
}

export function RepoAnalysis({ blurred = false }: RepoAnalysisProps) {
  return (
    <div className="rounded-large flex items-center justify-center">
      <div className="absolute z-50">
        <p className="font-bold text-2xl" />
      </div>
      <Card
        className={`w-full select-none ${blurred ? "blur-lg" : ""}`}
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
                AjayAntoIsDev
              </BreadcrumbItem>
              <BreadcrumbItem>SlopScan</BreadcrumbItem>
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
                      <div className="text-2xl font-bold text-warning">15%</div>
                      <div className="text-sm text-default-600">Use of AI</div>
                    </div>
                    <div className="text-center">
                      <Activity className="h-6 w-6 text-primary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-primary">156</div>
                      <div className="text-sm text-default-600">Commits</div>
                    </div>
                    <div className="text-center">
                      <XCircle className="h-6 w-6 text-danger mx-auto mb-2" />
                      <div className="text-2xl font-bold text-danger">12%</div>
                      <div className="text-sm text-default-600">Adequacy</div>
                    </div>
                  </div>
                </CardBody>
              </Card>

              <Card className="col-span-2 row-span-1 pb-2" radius="lg">
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
                      <div className="text-2xl font-bold text-success">23</div>
                      <div className="text-sm text-default-600">Devlogs</div>
                    </div>
                    <div className="text-center">
                      <Clock className="h-6 w-6 text-primary mx-auto mb-2" />
                      <div className="text-2xl font-bold text-primary">
                        4.2h
                      </div>
                      <div className="text-sm text-default-600">Avg Time</div>
                    </div>
                    <div className="text-center">
                      <Brain className="h-6 w-6 text-warning mx-auto mb-2" />
                      <div className="text-2xl font-bold text-warning">87%</div>
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
                      73
                      <span className="text-xs text-default-600">/100</span>
                    </div>
                  </div>

                  <div className="flex-1">
                    <ScrollShadow className="h-48 p-3 bg-default-50 rounded-lg">
                      <div className="space-y-2 text-xs">
                        <div className="flex flex-wrap gap-1 mb-3">
                          <Chip
                            className="text-xs px-2 py-0.5 h-5"
                            color="danger"
                            size="sm"
                            variant="flat"
                          >
                            Vague commits
                          </Chip>
                          <Chip
                            className="text-xs px-2 py-0.5 h-5"
                            color="warning"
                            size="sm"
                            variant="flat"
                          >
                            AI in README
                          </Chip>
                          <Chip
                            className="text-xs px-2 py-0.5 h-5"
                            color="success"
                            size="sm"
                            variant="flat"
                          >
                            Good devlogs
                          </Chip>
                        </div>
                        <p>
                          Lorem ipsum dolor sit amet, consectetur adipisicing
                          elit. Excepturi architecto pariatur maxime expedita
                          ullam aliquid recusandae iste minima qui, ducimus
                          dolorem sunt culpa? Ad rerum beatae repellendus
                          laboriosam officiis. Ab. Lorem ipsum dolor sit amet
                          consectetur adipisicing elit. Non ipsum eaque
                          architecto nobis voluptates dolorem commodi quidem.
                          Asperiores harum culpa nesciunt magnam eos impedit
                          fugit. Rerum sit expedita consequatur aperiam.
                        </p>
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

import { Input } from "@heroui/input";
import { Button } from "@heroui/button";
import { Accordion, AccordionItem } from "@heroui/accordion";
import {
  Settings,
  Brain,
  Code,
  HelpCircle,
  GitCommit,
  Activity,
  XCircle,
  BookOpen,
  Clock,
  FileText,
  Target,
  Zap,
  Copy,
} from "lucide-react";
import { Switch } from "@heroui/switch";
import { Select, SelectItem } from "@heroui/select";
import { NumberInput } from "@heroui/number-input";
import { Tooltip } from "@heroui/tooltip";
import { Card, CardHeader, CardBody } from "@heroui/card";
import { Image } from "@heroui/image";
import { Breadcrumbs, BreadcrumbItem } from "@heroui/breadcrumbs";
import { Chip } from "@heroui/chip";
import { ScrollShadow } from "@heroui/scroll-shadow";

import { SearchIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";
import DefaultLayout from "@/layouts/default";

export default function IndexPage() {
  return (
    <DefaultLayout>
      <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">
        <div className="inline-block max-w-lg text-center justify-center">
          <span className={title()}>Detect&nbsp;</span>
          <span className={title({ color: "blue" })}>Slop&nbsp;</span>
          <span className={title()}>with ease.</span>
          <div className={subtitle({ class: "mt-4" })}>
            AI powered slop detection tool that actually works
          </div>
        </div>

        <div className="w-3/6 mt-4 flex flex-col gap-4">
          <div className="flex gap-3 w-full">
            <Input
              isRequired
              labelPlacement="outside"
              name="repoUrl"
              placeholder="Enter GitHub repo or SoM project URL"
              type="url"
              validate={(value) => {
                if (!value) {
                  return "";
                }

                const githubPattern =
                  /^https:\/\/github\.com\/[\w\-\.]+\/[\w\-\.]+$/;
                const somPattern =
                  /^https:\/\/summer\.hackclub\.com\/projects\/\d+$/;

                if (!githubPattern.test(value) && !somPattern.test(value)) {
                  return "Must be a valid GitHub repo link or SoM project link";
                }

                return null;
              }}
            />
            <Button color="primary" type="submit">
              <SearchIcon className="h-5 w-5" />
            </Button>
          </div>
          <Accordion variant="splitted">
            <AccordionItem
              key="1"
              aria-label="Accordion 1"
              classNames=""
              indicator={<Settings />}
              title="Advanced Settings"
            >
              <div className="flex flex-col gap-6 p-2">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Switch
                        defaultSelected
                        color="primary"
                        endContent={<Code />}
                        size="lg"
                        startContent={<Brain />}
                      >
                        Enable AI Analysis
                      </Switch>
                    </div>
                    <Tooltip
                      content="Use AI for slop detection"
                      placement="top"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-500 cursor-help  transition-colors" />
                    </Tooltip>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Select
                      className="flex-1"
                      defaultSelectedKeys={["both"]}
                      label="Analysis Mode"
                      size="sm"
                      variant="bordered"
                    >
                      <SelectItem key={"both"}>
                        Repo Analysis + Code Analysis
                      </SelectItem>
                      <SelectItem key={"repo"}>Repo Analysis</SelectItem>
                      <SelectItem key={"code"}>Code Analysis</SelectItem>
                    </Select>
                    <Tooltip
                      content="Choose the type of analysis to perform"
                      placement="top"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-500 cursor-help  transition-colors" />
                    </Tooltip>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <NumberInput
                      className="flex-1"
                      defaultValue={50}
                      isDisabled={true}
                      label="Max files to analyze"
                      max={100}
                      min={1}
                      size="sm"
                      step={10}
                      variant="bordered"
                    />
                    <Tooltip
                      content="Limit the number of files to analyze to control processing time (Disabled coz i am too broke to pay for more 😭)"
                      placement="top"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-500 cursor-help  transition-colors" />
                    </Tooltip>
                  </div>
                </div>
              </div>
            </AccordionItem>
          </Accordion>
        </div>
        <div className="mt-4 w-full max-w-6xl mx-auto">
          <div className="mb-6 flex justify-center">
            <div className="text-center">
              <div className="text-5xl font-bold text-danger">
                79
                <span className="text-sm text-default-600">/100</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="border-1 border-gray-950 rounded-large">
              <Card className="w-full blur-" radius="lg">
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
                              <div className="text-2xl font-bold text-warning">
                                15%
                              </div>
                              <div className="text-sm text-default-600">
                                Use of AI
                              </div>
                            </div>
                            <div className="text-center">
                              <Activity className="h-6 w-6 text-primary mx-auto mb-2" />
                              <div className="text-2xl font-bold text-primary">
                                156
                              </div>
                              <div className="text-sm text-default-600">
                                Commits
                              </div>
                            </div>
                            <div className="text-center">
                              <XCircle className="h-6 w-6 text-danger mx-auto mb-2" />
                              <div className="text-2xl font-bold text-danger">
                                12%
                              </div>
                              <div className="text-sm text-default-600">
                                Adequacy
                              </div>
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
                              <div className="text-2xl font-bold text-success">
                                23
                              </div>
                              <div className="text-sm text-default-600">
                                Devlogs
                              </div>
                            </div>
                            <div className="text-center">
                              <Clock className="h-6 w-6 text-primary mx-auto mb-2" />
                              <div className="text-2xl font-bold text-primary">
                                4.2h
                              </div>
                              <div className="text-sm text-default-600">
                                Avg Time
                              </div>
                            </div>
                            <div className="text-center">
                              <Brain className="h-6 w-6 text-warning mx-auto mb-2" />
                              <div className="text-2xl font-bold text-warning">
                                87%
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
                              73
                              <span className="text-xs text-default-600">
                                /100
                              </span>
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
                                  Lorem ipsum dolor sit amet, consectetur
                                  adipisicing elit. Excepturi architecto
                                  pariatur maxime expedita ullam aliquid
                                  recusandae iste minima qui, ducimus dolorem
                                  sunt culpa? Ad rerum beatae repellendus
                                  laboriosam officiis. Ab. Lorem ipsum dolor sit
                                  amet consectetur adipisicing elit. Non ipsum
                                  eaque architecto nobis voluptates dolorem
                                  commodi quidem. Asperiores harum culpa
                                  nesciunt magnam eos impedit fugit. Rerum sit
                                  expedita consequatur aperiam.
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

            {/* Code Analysis Card - Empty space for now */}
            <div className="w-full">
              <Card className="w-full blur- h-full flex" radius="lg">
                <CardBody className="pt-2">
                  <div className="flex flex-col gap-4 justify-center items-center h-full">
                    <div className="flex flex-col gap-4 w-full">
                      <Card className="col-span-2 row-span-1 pb-2" radius="lg">
                        <CardHeader className="pb-2">
                          <div className="flex items-center gap-2">
                            <Code className="h-5 w-5 text-secondary" />
                            <h3 className="text-lg font-bold">Code Analysis</h3>
                          </div>
                        </CardHeader>

                        <CardBody>
                          <div className="grid grid-cols-3 gap-4 w-full">
                            <div className="text-center">
                              <Brain className="h-6 w-6 text-primary mx-auto mb-2" />
                              <div className="text-2xl font-bold text-primary">
                                8.2
                              </div>
                              <div className="text-sm text-default-600">
                                AI in code
                              </div>
                            </div>
                            <div className="text-center">
                              <Zap className="h-6 w-6 text-secondary mx-auto mb-2" />
                              <div className="text-2xl font-bold text-secondary">
                                94%
                              </div>
                              <div className="text-sm text-default-600">
                                Perfectness
                              </div>
                            </div>
                            <div className="text-center">
                              <Copy className="h-6 w-6 text-warning mx-auto mb-2" />
                              <div className="text-2xl font-bold text-warning">
                                23%
                              </div>
                              <div className="text-sm text-default-600">
                                Unused Code
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
                            <Target className="h-5 w-5 text-primary" />
                            <h3 className="text-lg font-bold">SlopScore</h3>
                          </div>
                        </CardHeader>

                        <CardBody className="grid grid-cols-4 grid-rows-1 gap-4">
                          <div className="text-center flex items-center justify-center">
                            <div className="text-5xl font-bold text-primary">
                              85
                              <span className="text-xs text-default-600">
                                /100
                              </span>
                            </div>
                          </div>
                          <div className="flex flex-col gap-1 justify-center">
                            <Chip
                              className="text-xs px-2 py-0.5 h-5"
                              color="primary"
                              size="sm"
                              variant="flat"
                            >
                              Clean structure
                            </Chip>
                            <Chip
                              className="text-xs px-2 py-0.5 h-5"
                              color="warning"
                              size="sm"
                              variant="flat"
                            >
                              Some duplicates
                            </Chip>
                            <Chip
                              className="text-xs px-2 py-0.5 h-5"
                              color="secondary"
                              size="sm"
                              variant="flat"
                            >
                              Good performance
                            </Chip>
                          </div>
                          <div className="col-span-2">
                            <ScrollShadow className="h-32 p-3 bg-default-50 rounded-lg">
                              <div className="space-y-2 text-xs">
                                Lorem ipsum dolor sit amet, consectetur
                                adipisicing elit. Excepturi architecto pariatur
                                maxime expedita ullam aliquid recusandae iste
                                minima qui, ducimus dolorem sunt culpa? Ad rerum
                                beatae repellendus laboriosam officiis. Ab.
                                Lorem ipsum dolor sit amet consectetur
                                adipisicing elit. Non ipsum eaque architecto
                                nobis voluptates dolorem commodi quidem.
                                Asperiores harum culpa nesciunt magnam eos
                                impedit fugit. Rerum sit expedita consequatur
                                aperiam.
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
          </div>
        </div>
      </section>
    </DefaultLayout>
  );
}

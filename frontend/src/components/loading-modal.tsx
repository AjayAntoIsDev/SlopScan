import { Modal, ModalContent, ModalHeader, ModalBody } from "@heroui/modal";
import { Progress } from "@heroui/progress";
import { Loader2 } from "lucide-react";

interface LoadingModalProps {
  isOpen: boolean;
  onClose: () => void;
  progress: number;
  status: string;
  url: string;
}

export function LoadingModal({
  isOpen,
  onClose,
  progress,
  status,
  url,
}: LoadingModalProps) {
  return (
    <Modal
      hideCloseButton={true}
      isDismissable={false}
      isOpen={isOpen}
      size="lg"
      onClose={onClose}
    >
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h3 className="text-xl font-semibold">Analyzing Repository</h3>
          <p className="text-sm text-default-500 truncate">{url}</p>
        </ModalHeader>
        <ModalBody className="pb-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <span className="text-sm font-medium">{status}</span>
            </div>

            <Progress
              className="w-full"
              color="primary"
              showValueLabel={true}
              size="md"
              value={progress}
            />

            <div className="mt-2">
              <p className="text-xs text-default-400">
                This may take a few minutes depending on the repository size...
              </p>
            </div>
          </div>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
}

import { KeyboardEvent, useEffect, useRef } from "react";

const FOCUSABLE = [
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[href]",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

export function useDialogFocusReturn() {
  const returnTarget = useRef<HTMLElement | null>(
    document.activeElement instanceof HTMLElement ? document.activeElement : null,
  );

  useEffect(() => () => {
    if (returnTarget.current?.isConnected) returnTarget.current.focus();
  }, []);
}

export function trapDialogFocus(event: KeyboardEvent<HTMLDivElement>) {
  if (event.key !== "Tab") return;
  const controls = Array.from(event.currentTarget.querySelectorAll<HTMLElement>(FOCUSABLE));
  if (!controls.length) return;
  const first = controls[0];
  const last = controls.at(-1)!;
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

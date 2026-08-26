import React, { useCallback, useState } from "react";
import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  User,
  Chip,
  Tooltip,
  useDisclosure,
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  addToast,
} from "@heroui/react";
import { GrRestroomMen, GrRestroomWomen } from "react-icons/gr";
import { FaHome } from "react-icons/fa";
import { PiIslandBold } from "react-icons/pi";
import { useNavigate } from "react-router";

export const columns = [
  { name: "USUARIO", uid: "nombre" },
  { name: "EDAD", uid: "edad" },
  { name: "SEXO", uid: "sexo" },
  { name: "LOCALIDAD", uid: "localidad" },
  { name: "AMBIENTE", uid: "ambiente" },
  { name: "STATUS", uid: "status" },
  { name: "CREADO", uid: "created_at" },
  { name: "ACCIONES", uid: "actions" },
];

export const EyeIcon = (props: any) => {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      focusable="false"
      height="1em"
      role="presentation"
      viewBox="0 0 20 20"
      width="1em"
      {...props}
    >
      <path
        d="M12.9833 10C12.9833 11.65 11.65 12.9833 10 12.9833C8.35 12.9833 7.01666 11.65 7.01666 10C7.01666 8.35 8.35 7.01666 10 7.01666C11.65 7.01666 12.9833 8.35 12.9833 10Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
      <path
        d="M9.99999 16.8916C12.9417 16.8916 15.6833 15.1583 17.5917 12.1583C18.3417 10.9833 18.3417 9.00831 17.5917 7.83331C15.6833 4.83331 12.9417 3.09998 9.99999 3.09998C7.05833 3.09998 4.31666 4.83331 2.40833 7.83331C1.65833 9.00831 1.65833 10.9833 2.40833 12.1583C4.31666 15.1583 7.05833 16.8916 9.99999 16.8916Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
    </svg>
  );
};

export const DeleteIcon = (props: any) => {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      focusable="false"
      height="1em"
      role="presentation"
      viewBox="0 0 20 20"
      width="1em"
      {...props}
    >
      <path
        d="M17.5 4.98332C14.725 4.70832 11.9333 4.56665 9.15 4.56665C7.5 4.56665 5.85 4.64998 4.2 4.81665L2.5 4.98332"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
      <path
        d="M7.08331 4.14169L7.26665 3.05002C7.39998 2.25835 7.49998 1.66669 8.90831 1.66669H11.0916C12.5 1.66669 12.6083 2.29169 12.7333 3.05835L12.9166 4.14169"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
      <path
        d="M15.7084 7.61664L15.1667 16.0083C15.075 17.3166 15 18.3333 12.675 18.3333H7.32502C5.00002 18.3333 4.92502 17.3166 4.83335 16.0083L4.29169 7.61664"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
      <path
        d="M8.60834 13.75H11.3833"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
      <path
        d="M7.91669 10.4167H12.0834"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
      />
    </svg>
  );
};

interface UsersTableProps {
  users: Array<any>;
  isLoading: boolean;
  onDeleteUser: () => {}
}

export default function UsersTable({ users, isLoading, onDeleteUser }: UsersTableProps) {
  const navigate = useNavigate();
  const { isOpen, onClose, onOpenChange, onOpen } = useDisclosure();
  const [loading, setLoading] = useState(false);
  const [userToDelete, setUserToDelete] = useState(null)
  const apiUrl = import.meta.env.VITE_API_URL;

  const deleteUser = async () => {
    if(userToDelete) {
        setLoading(true);
        await fetch(`${apiUrl}/api/delete-user`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ id: userToDelete }),
        })
          .then((res) => res.json())
          .then((res) => {
            if (res.deleted) {
              addToast({
                title: "Eliminado correctamente",
                description: "Se ha eliminado el usuario",
                color: "success",
              });
            }
          })
          .finally(() => {
            setLoading(false);
            onDeleteUser()
            onClose()
          });

        setUserToDelete(null);
    }
  };

  const renderCell = useCallback(
    (user, columnKey) => {
      const cellValue = user[columnKey];

      switch (columnKey) {
        case "nombre":
          return (
            <div className="fle flex-col">
              <h3 className="font-bold">{user?.nombre}</h3>
              <p className="text-small text-default-400">{user?.contacto}</p>
            </div>
          );
        case "edad":
          return (
            <Chip color="warning" variant="bordered" size="sm">
              {user?.edad} años
            </Chip>
          );
        case "sexo":
          return (
            <Chip
              color={user?.sexo === "mujer" ? "secondary" : "success"}
              endContent={
                user?.sexo === "mujer" ? (
                  <GrRestroomWomen className="size-5" />
                ) : (
                  <GrRestroomMen className="size-5" />
                )
              }
              variant="flat"
              className="px-4"
              size="sm"
            >
              {user?.sexo}
            </Chip>
          );
        case "ambiente":
          return (
            <Chip
              color={user?.ambiente === "interior" ? "success" : "warning"}
              endContent={
                user?.ambiente === "interior" ? (
                  <FaHome className="size-5" />
                ) : (
                  <PiIslandBold className="size-5" />
                )
              }
              variant="flat"
              className="px-4"
              size="sm"
            >
              {user?.ambiente}
            </Chip>
          );
        case "status":
          return (
            <Chip
              className="capitalize"
              color={user.status === "complete" ? "success" : "warning"}
              size="sm"
              variant="flat"
            >
              {cellValue}
            </Chip>
          );
        case "created_at":
          const fecha = new Date(cellValue);
          const formateada = new Intl.DateTimeFormat("es-ES", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
          }).format(fecha);
          return formateada;
        case "actions":
          return (
            <div className="relative flex items-center justify-evenly gap-2 w-full">
              <Tooltip content="Details">
                <span
                  className="text-lg text-default-400 cursor-pointer active:opacity-50"
                  onClick={() => navigate(`/user/${user?.id}`)}
                >
                  <EyeIcon />
                </span>
              </Tooltip>
              <Tooltip color="danger" content="Delete user">
                <span
                  className="text-lg text-danger cursor-pointer active:opacity-50"
                  onClick={() => {
                    setUserToDelete(user?.id);
                    onOpen();
                  }}
                >
                  <DeleteIcon />
                </span>
              </Tooltip>
            </div>
          );
        default:
          return cellValue;
      }
    },
    [users]
  );

  return (
    <>
      <Table aria-label="Example table with custom cells">
        <TableHeader columns={columns}>
          {(column) => (
            <TableColumn
              key={column.uid}
              align={column.uid === "actions" ? "center" : "start"}
            >
              {column.name}
            </TableColumn>
          )}
        </TableHeader>
        <TableBody
          items={users || []}
          isLoading={isLoading}
          emptyContent={"No hay usuarios registrados"}
          className="items-center"
        >
          {(item) => (
            <TableRow key={item.id}>
              {(columnKey) => (
                <TableCell>{renderCell(item, columnKey)}</TableCell>
              )}
            </TableRow>
          )}
        </TableBody>
      </Table>
      <Modal isOpen={isOpen} onOpenChange={onOpenChange} size="lg">
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">
                Eliminar Usuario
              </ModalHeader>
              <ModalBody className="w-full" key="modal body">
                <h5>¿Quieres eliminar a este usuario?</h5>
              </ModalBody>
              <ModalFooter className="w-full" key="modal footer">
                <Button color="danger" variant="light" onPress={onClose}>
                  Cerrar
                </Button>
                <Button
                  color="danger"
                  onPress={deleteUser}
                >
                  Eliminar
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );
}

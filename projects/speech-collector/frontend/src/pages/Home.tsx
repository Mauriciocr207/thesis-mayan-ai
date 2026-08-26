import { useEffect, useState } from "react";
import UsersTable from "../components/UsersTable";
import {
  Button,
  Form,
  Input,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  Select,
  SelectItem,
  Textarea,
  useDisclosure,
} from "@heroui/react";
import { FaPlusCircle } from "react-icons/fa";
import { useNavigate } from "react-router";

export default function Home() {
  const apiUrl = import.meta.env.VITE_API_URL;
  const appName = import.meta.env.VITE_APP_TITLE || "Sound Collector App";

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isOpen, onOpen, onOpenChange } = useDisclosure();
  const navigate = useNavigate();

  // function which gets task from the server
  const getUsers = async () => {
    setLoading(true);
    await fetch(`${apiUrl}/api/get-users`)
      .then((res) => res.json())
      .then((users) => {
        setUsers(users);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const createUser = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const userData = Object.fromEntries(formData.entries());
    setLoading(true);
    await fetch(`${apiUrl}/api/add-user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.status) {
          navigate(`/user/${res.id}`);
        }
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    getUsers();
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 xl:max-w-5xl xl:px-0">
      <header className="flex items-center w-full bg-white dark:bg-gray-950 justify-between py-10">
        <a className="wrap-break-word" aria-label="TailwindBlog" href="/">
          <div className="flex items-center justify-between">
            <div className="mr-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                xmlnsXlink="http://www.w3.org/1999/xlink"
                width="53.87"
                height="43.61"
                viewBox="344.564 330.278 111.737 91.218"
              >
                <defs>
                  <linearGradient
                    id="logo_svg__b"
                    x1="420.97"
                    x2="420.97"
                    y1="331.28"
                    y2="418.5"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop
                      offset="0%"
                      style={{ stopColor: "#06b6d4", stopOpacity: 1 }}
                    />
                    <stop
                      offset="100%"
                      style={{ stopColor: "#67e8f9", stopOpacity: 1 }}
                    />
                  </linearGradient>

                  <linearGradient
                    id="logo_svg__d"
                    x1="377.89"
                    x2="377.89"
                    y1="331.28"
                    y2="418.5"
                    gradientUnits="userSpaceOnUse"
                  >
                    <stop
                      offset="0%"
                      style={{ stopColor: "#06b6d4", stopOpacity: 1 }}
                    />
                    <stop
                      offset="100%"
                      style={{ stopColor: "#67e8f9", stopOpacity: 1 }}
                    />
                  </linearGradient>

                  <path
                    id="logo_svg__a"
                    d="M453.3 331.28v28.57l-64.66 58.65v-30.08z"
                  />
                  <path
                    id="logo_svg__c"
                    d="M410.23 331.28v28.57l-64.67 58.65v-30.08z"
                  />
                </defs>

                <use xlinkHref="#logo_svg__a" fill="url(#logo_svg__b)" />
                <use xlinkHref="#logo_svg__c" fill="url(#logo_svg__d)" />
              </svg>
            </div>
            <div className="hidden h-6 text-2xl font-semibold sm:block">
              Voice Recorder
            </div>
          </div>
        </a>
        <div className="flex items-center space-x-4 leading-5 sm:-mr-6 sm:space-x-6">
          <div className="no-scrollbar hidden max-w-40 items-center gap-x-4 overflow-x-auto sm:flex md:max-w-72 lg:max-w-96">
            <Button variant="solid" color="primary" onPress={onOpen}>
              Crear usuario <FaPlusCircle />
            </Button>
            <Modal isOpen={isOpen} onOpenChange={onOpenChange} size="lg">
              <ModalContent>
                {(onClose) => (
                  <>
                    <ModalHeader className="flex flex-col gap-1">
                      Nuevo Usuario
                    </ModalHeader>
                    <ModalBody className="w-full" key="modal body">
                      <Form
                        onSubmit={createUser}
                        className="w-full flex flex-col gap-5"
                        id="create-user-form"
                      >
                        <div className="flex w-full gap-3">
                          <Input
                            isRequired
                            errorMessage="Escribe un nombre"
                            label="Nombre"
                            labelPlacement="outside"
                            name="nombre"
                            placeholder="Ingresa tu nombre"
                            type="text"
                            className="basis-2/3"
                          />
                          <Input
                            isRequired
                            errorMessage="Escribe una edad válida"
                            min={0}
                            max={100}
                            label="Edad"
                            labelPlacement="outside"
                            name="edad"
                            placeholder="Ingres tu edad"
                            type="number"
                            className="basis-1/3"
                          />
                        </div>
                        <div className="flex w-full gap-3 items-start">
                          <Select
                            isRequired
                            items={[
                              { key: "mujer", label: "mujer" },
                              { key: "hombre", label: "hombre" },
                            ]}
                            label="Sexo"
                            name="sexo"
                            placeholder="Selecciona"
                            size="md"
                            labelPlacement="outside"
                            errorMessage="Selecciona un sexo"
                          >
                            {[
                              { key: "mujer", label: "mujer" },
                              { key: "hombre", label: "hombre" },
                            ].map((option) => (
                              <SelectItem key={option.key}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </Select>
                          <Input
                            errorMessage="Localidad requerida"
                            label="Localidad"
                            labelPlacement="outside"
                            name="localidad"
                            placeholder="Ingresa tu localidad"
                            type="text"
                          />
                        </div>
                        <div className="flex w-full gap-3">
                          <Select
                            isRequired
                            items={[
                              { key: "interior", label: "interior" },
                              { key: "exterior", label: "exterior" },
                            ]}
                            label="Ambiente"
                            placeholder="Selecciona"
                            size="md"
                            labelPlacement="outside"
                            errorMessage="Selecciona un ambiente"
                            name="ambiente"
                          >
                            {[
                              { key: "interior", label: "interior" },
                              { key: "exterior", label: "exterior" },
                            ].map((option) => (
                              <SelectItem key={option.key}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </Select>
                          <Input
                            errorMessage="Contacto requerido"
                            label="Contacto"
                            labelPlacement="outside"
                            name="contacto"
                            placeholder="Ingresa un contacto"
                            type="text"
                          />
                        </div>
                        <Textarea
                          className="w-full"
                          label="Observaciones"
                          name="observaciones"
                          labelPlacement="outside"
                          placeholder="Ingresa una descripción (opcional)"
                        />
                      </Form>
                    </ModalBody>
                    <ModalFooter className="w-full" key="modal footer">
                      <Button color="danger" variant="light" onPress={onClose}>
                        Cerrar
                      </Button>
                      <Button
                        color="primary"
                        form={"create-user-form"}
                        type="submit"
                        disabled={loading}
                        isLoading={loading}
                      >
                        Crear
                      </Button>
                    </ModalFooter>
                  </>
                )}
              </ModalContent>
            </Modal>
          </div>
        </div>
      </header>
      <UsersTable users={users} isLoading={loading} onDeleteUser={getUsers} />
    </div>
  );
}

import { Button, Chip, Divider } from "@heroui/react";
import { useEffect, useState } from "react";
import { FaHome } from "react-icons/fa";
import { GrRestroomWomen, GrRestroomMen } from "react-icons/gr";
import { PiIslandBold } from "react-icons/pi";
import { Link, useParams } from "react-router";
import { FiEdit3 } from "react-icons/fi";
import RecordSlider from "../components/RecordSlider";

export default function Record() {
  const apiUrl = import.meta.env.VITE_API_URL;
  const params = useParams();
  const userId = params.userId;
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await fetch(`${apiUrl}/api/get-user?userId=${userId}`);
        const data = await response.json();
        setUser(data);
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    }
    fetchUser();
  }, []);

  return (
    <div className="mx-auto px-4 sm:px-6 max-w-5xl xl:px-0">
      <header className="flex items-center w-full bg-white dark:bg-gray-950 justify-between py-10">
        <Link className="wrap-break-word" aria-label="TailwindBlog" to="/">
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
        </Link>
        <div className="flex items-center space-x-4 leading-5 sm:-mr-6 sm:space-x-6">
          <div className="no-scrollbar hidden max-w-40 items-center gap-x-4 overflow-x-auto sm:flex md:max-w-72 lg:max-w-96">
            <Button variant="solid" color="primary">
              Editar usuario <FiEdit3 />
            </Button>
          </div>
        </div>
      </header>
      <main className="w-full">
        <div className="w-full">
          <div className="space-y-1 flex items-start w-full justify-between">
            <div>
              <h4 className="text-medium font-medium">{user?.nombre}</h4>
              <p className="text-small text-default-400">
                {user?.observaciones}
              </p>
            </div>
            <div>
              <p className="text-small text-default-400">
                Localidad:{" "}
                <span className="text-small text-default-400">
                  {user?.localidad}
                </span>
              </p>
              <p className="text-small text-default-400">
                Contacto:{" "}
                <span className="text-small text-default-400">
                  {user?.contacto}
                </span>
              </p>
            </div>
          </div>
          <Divider className="my-4" />
          <div className="flex h-5 items-center space-x-4 text-small">
            <Chip color="warning" variant="bordered">
              {user?.edad} años
            </Chip>
            <Divider orientation="vertical" />
            <div>
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
              >
                {user?.sexo}
              </Chip>
            </div>
            <Divider orientation="vertical" />
            <div>
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
                size="md"
              >
                {user?.ambiente}
              </Chip>
            </div>
          </div>
        </div>
      </main>
      <section className="mt-10">
        <RecordSlider />
      </section>
    </div>
  );
}

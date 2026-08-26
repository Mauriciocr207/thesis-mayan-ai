import { Swiper, SwiperSlide } from "swiper/react";
import { Swiper as SwiperType } from "swiper";
import { EffectCoverflow } from "swiper/modules";
import "swiper/css";
import { Button, Checkbox, Tooltip } from "@heroui/react";
import { useEffect, useRef, useState } from "react";
import { useVoiceVisualizer, VoiceVisualizer } from "react-voice-visualizer";
import useRecordHandler from "../hooks/useRecordHandler";

export default function RecordSlider() {
  const [frases, setFrases] = useState<string[]>([]);
  const swiperRef = useRef<SwiperType | null>(null);
  const controls = useVoiceVisualizer();
  const { records, setFileToRecord } = useRecordHandler(frases);
  const [currentIndex, setCurrentIndex] = useState(0);

  const apiUrl = import.meta.env.VITE_API_URL;

  useEffect(() => {
    async function fetchFrases() {
      try {
        const response = await fetch(`${apiUrl}/api/get-phrases`);
        const data = await response.json();
        const mayan_frases: string[] = data.map(
          (row: { mayan_text: string }) => row.mayan_text
        );
        setFrases(mayan_frases);
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    }
    fetchFrases();
  }, []);

  useEffect(() => {
    if(controls.recordedBlob) {
        setFileToRecord(currentIndex, controls.recordedBlob);
    }
  }, [controls.recordedBlob])

  useEffect(() => {
    if(controls.isCleared) {
        setFileToRecord(currentIndex, null);
    }
  }, [controls.isCleared])

  useEffect(() => {
    toSlide(currentIndex);
    if(records?.[currentIndex]?.file) {
        controls.setPreloadedAudioBlob(records[currentIndex].file);
    } else {
      controls.clearCanvas();
    }
  }, [currentIndex])
  
  useEffect(() => {
    console.log(records);
  }, [records]);

  function toSlide(index: number) {
    if (swiperRef.current) {
      swiperRef.current.slideTo(index);
    }
  };

  function handleCheckedRecord(isSelected: boolean) {
    if(isSelected) {
        setCurrentIndex((currentIndex) => {
            if(currentIndex < records.length - 1) {
                return currentIndex + 1;
            }

            return currentIndex;
        })
    }
  }



  return (
    <div className="w-full">
      <div className="h-[350px] w-full grid grid-rows-10 grid-cols-10">
        <div className="w-full h-full col-start-1 col-end-9 row-start-1 row-span-10">
          <Swiper
            slidesPerView={3}
            effect="coverflow"
            spaceBetween={30}
            centeredSlides={true}
            coverflowEffect={{
              rotate: 50,
              stretch: 0,
              depth: 100,
            }}
            modules={[EffectCoverflow]}
            className="h-full w-full"
            onSwiper={(swiper: any) => (swiperRef.current = swiper)}
          >
            {frases.map((text) => (
              <SwiperSlide key={text}>
                <div className="flex items-center justify-center w-full h-full shadow p-2">
                  <p className="text-3xl text-center">{text}</p>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </div>
        <div className="w-full h-full row-span-10 col-span-2 flex flex-col gap-4 overflow-y-auto p-2">
          {frases.map((_, index) => (
            <Tooltip
              content="Graba un audio para completa esta frase"
              key={index}
            >
              <Button
                color="primary"
                className="min-h-10 min-w-full flex justify-between items-center"
                onPress={() => setCurrentIndex(index)}
                variant="bordered"
              >
                <p className="text-sm">Frase {index + 1}</p>
                <Checkbox
                  size="md"
                  className="p-0 border-primary"
                  color="primary"
                  classNames={{ 
                    icon: "text-white",
                    label: `${records?.[index]?.file ? "active-checkbox": ""}`
                 }}
                  isDisabled={!records?.[index]?.file}
                  onValueChange={handleCheckedRecord}
                />
              </Button>
            </Tooltip>
          ))}
        </div>
      </div>
      <VoiceVisualizer
        controls={controls}
        height={100}
        mainBarColor="black"
        secondaryBarColor="#5e5e5e"
        defaultMicrophoneIconColor="black"
        defaultAudioWaveIconColor="black"
      />
    </div>
  );
}

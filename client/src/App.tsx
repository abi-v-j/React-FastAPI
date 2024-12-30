import React, { useState, ChangeEvent, FormEvent } from "react";
import axios from "axios";

interface FormData {
  photo: File | null;
  name: string;
  email: string;
}

const App: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    photo: null,
    name: "",
    email: "",
  });

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value, files } = e.target;
    if (name === "photo" && files) {
      setFormData({ ...formData, photo: files[0] });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const data = new FormData();
    if (formData.photo) {
      data.append("photo", formData.photo);
    }
    data.append("name", formData.name);
    data.append("email", formData.email);

    try {
      const response = await axios.post("http://127.0.0.1:8000/users", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Response:", response.data);
    } catch (error) {
      console.error("Error uploading form data:", error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          name="photo"
          onChange={handleChange}
        />
        <input
          type="text"
          name="name"
          placeholder="Name"
          value={formData.name}
          onChange={handleChange}
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
        />
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default App;

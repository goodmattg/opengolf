use burn_import::onnx::ModelGen;

fn main() {
    ModelGen::new()
        .development(true)
        .input("models/FLUX.1-Depth-dev-onnx/transformer.opt/bf16/model.onnx")
        .out_dir("src/model/")
        .run_from_script();

    tauri_build::build()
}

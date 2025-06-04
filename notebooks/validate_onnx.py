import onnx


if __name__ == "__main__":
    model_path = (
        "../src-tauri/models/FLUX.1-Depth-dev-onnx/transformer.opt/bf16/model.onnx"
    )
    model = onnx.load(model_path)

    for node in model.graph.node:
        if node.name == "MatMul_19916":
            print(node)
